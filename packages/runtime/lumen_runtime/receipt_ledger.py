"""Clean-room single-owner ReceiptLedger — candidate implementation of ADR-0006.

Governance status: CANDIDATE. This module does not close C-RCPT-001. Closure
requires steward disposition, a clean-clone repair receipt, and a gate decision.
Presence of this file is not evidence of repair.

Canonicalization profile: LNX-RECEIPT-CJSON-1. This is not PG001R-JSON-1 and
not triweavon-cjson-v1. It is the frozen receipt-core profile for linkage bytes.
"""

from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass
from typing import Any, Iterable

CANON_PROFILE = "LNX-RECEIPT-CJSON-1"
GENESIS_PREDECESSOR = "0" * 64


class LedgerError(Exception):
    """Raised when an append violates a frozen ledger invariant."""


def _canonical_bytes(payload: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes or fail closed.

    The profile uses sorted object keys, minimal separators, native Unicode,
    and rejects NaN/Infinity and unsupported values.
    """

    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise LedgerError(f"event content is not canonicalizable: {exc}") from exc


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Receipt:
    """A committed immutable receipt and its retained canonical event bytes.

    ``witness_identity_binding`` is intentionally absent from the append API.
    Witness eligibility belongs to a separately verified receipt envelope and
    cannot be asserted by an origin caller.
    """

    seq: int
    predecessor_digest: str
    event_canonical_bytes: bytes
    event_canonical_sha256: str
    receipt_digest: str
    canon_profile: str = CANON_PROFILE
    witness_identity_binding: None = None

    def core(self) -> dict[str, Any]:
        """Return the exact metadata fields hashed into ``receipt_digest``."""

        return {
            "seq": self.seq,
            "predecessor_digest": self.predecessor_digest,
            "event_canonical_sha256": self.event_canonical_sha256,
            "canon_profile": self.canon_profile,
            "witness_identity_binding": self.witness_identity_binding,
        }


def _materialize(seq: int, predecessor_digest: str, canonical: bytes) -> Receipt:
    event_hash = _sha256_hex(canonical)
    core = {
        "seq": seq,
        "predecessor_digest": predecessor_digest,
        "event_canonical_sha256": event_hash,
        "canon_profile": CANON_PROFILE,
        "witness_identity_binding": None,
    }
    digest = _sha256_hex(_canonical_bytes(core))
    return Receipt(
        seq=seq,
        predecessor_digest=predecessor_digest,
        event_canonical_bytes=bytes(canonical),
        event_canonical_sha256=event_hash,
        receipt_digest=digest,
    )


class ReceiptLedger:
    """Sole owner of mutable linkage state.

    Appends are serialized under one lock. This guarantees one gapless,
    unambiguous committed order (linearizability), not reproducible scheduling
    order across independent concurrent executions.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._chain: list[Receipt] = []
        self._head_digest = GENESIS_PREDECESSOR
        self._next_seq = 0

    def append(
        self,
        event_content: Any,
        *,
        expected_predecessor: str | None = None,
    ) -> Receipt:
        """Canonicalize and atomically commit one event.

        Callers supply logical content only. ``expected_predecessor`` is an
        optimistic-concurrency assertion; it never lets callers choose linkage.
        """

        canonical = _canonical_bytes(event_content)
        with self._lock:
            if (
                expected_predecessor is not None
                and expected_predecessor != self._head_digest
            ):
                raise LedgerError(
                    "predecessor mismatch: ledger advanced or caller is stale "
                    f"(expected {expected_predecessor[:12]}…, "
                    f"actual {self._head_digest[:12]}…)"
                )

            seq = self._next_seq
            receipt = _materialize(seq, self._head_digest, canonical)

            # Commit only after canonicalization and materialization succeed.
            self._chain.append(receipt)
            self._head_digest = receipt.receipt_digest
            self._next_seq = seq + 1
            return receipt

    def head(self) -> str:
        with self._lock:
            return self._head_digest

    def length(self) -> int:
        with self._lock:
            return len(self._chain)

    def snapshot(self) -> tuple[Receipt, ...]:
        """Return an immutable point-in-time view."""

        with self._lock:
            return tuple(self._chain)


def verify_chain(snapshot: Iterable[Receipt]) -> bool:
    """Purely verify event hashes, receipt digests, sequencing, and linkage."""

    expected_predecessor = GENESIS_PREDECESSOR
    try:
        receipts = tuple(snapshot)
        for index, receipt in enumerate(receipts):
            if receipt.seq != index:
                return False
            if receipt.predecessor_digest != expected_predecessor:
                return False
            if receipt.canon_profile != CANON_PROFILE:
                return False
            if receipt.witness_identity_binding is not None:
                return False
            if _sha256_hex(receipt.event_canonical_bytes) != receipt.event_canonical_sha256:
                return False
            if _sha256_hex(_canonical_bytes(receipt.core())) != receipt.receipt_digest:
                return False
            expected_predecessor = receipt.receipt_digest
    except (AttributeError, LedgerError, TypeError):
        return False
    return True


def replay(events: Iterable[Any]) -> ReceiptLedger:
    """Deterministically rebuild a ledger from a sequential event stream."""

    ledger = ReceiptLedger()
    for event in events:
        ledger.append(event)
    return ledger
