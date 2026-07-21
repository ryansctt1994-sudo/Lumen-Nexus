"""ADR-0006 required-evidence suite for the candidate ReceiptLedger."""

from __future__ import annotations

import dataclasses
import threading

import pytest

from packages.runtime.lumen_runtime.receipt_ledger import (
    CANON_PROFILE,
    GENESIS_PREDECESSOR,
    LedgerError,
    Receipt,
    ReceiptLedger,
    _canonical_bytes,
    replay,
    verify_chain,
)


def test_positive_append_links_retains_bytes_and_verifies():
    ledger = ReceiptLedger()
    first = ledger.append({"kind": "genesis"})
    second = ledger.append({"kind": "next", "n": 1})

    assert first.seq == 0
    assert first.predecessor_digest == GENESIS_PREDECESSOR
    assert first.event_canonical_bytes == b'{"kind":"genesis"}'
    assert second.seq == 1
    assert second.predecessor_digest == first.receipt_digest
    assert verify_chain(ledger.snapshot())


def test_replay_is_deterministic_for_sequential_events():
    events = [{"k": i} for i in range(10)]
    left = replay(events).snapshot()
    right = replay(events).snapshot()
    assert [r.receipt_digest for r in left] == [r.receipt_digest for r in right]
    assert verify_chain(left)


def test_predecessor_mismatch_fails_closed():
    ledger = ReceiptLedger()
    ledger.append({"k": 0})
    with pytest.raises(LedgerError):
        ledger.append({"k": 1}, expected_predecessor=GENESIS_PREDECESSOR)


def test_sequence_is_ledger_owned_not_payload_owned():
    ledger = ReceiptLedger()
    ledger.append({"seq": 999, "payload": "attempt to spoof sequence"})
    assert ledger.snapshot()[0].seq == 0


def test_noncanonical_numbers_fail_without_advancing_state():
    ledger = ReceiptLedger()
    ledger.append({"k": 0})
    head_before = ledger.head()
    length_before = ledger.length()

    with pytest.raises(LedgerError):
        ledger.append({"bad": float("nan")})
    with pytest.raises(LedgerError):
        ledger.append({"bad": float("inf")})

    assert ledger.head() == head_before
    assert ledger.length() == length_before


def test_ingress_mutation_cannot_change_retained_bytes():
    ledger = ReceiptLedger()
    event = {"k": "v", "nested": ["a"]}
    receipt = ledger.append(event)
    retained = receipt.event_canonical_bytes

    event["k"] = "TAMPERED"
    event["nested"].append("b")

    assert receipt.event_canonical_bytes == retained
    assert verify_chain(ledger.snapshot())


def test_snapshot_is_fixed_and_receipts_are_frozen():
    ledger = ReceiptLedger()
    receipt = ledger.append({"k": 0})
    snapshot = ledger.snapshot()
    ledger.append({"k": 1})

    assert len(snapshot) == 1
    with pytest.raises(dataclasses.FrozenInstanceError):
        receipt.seq = 5


def test_event_byte_corruption_is_detected():
    ledger = ReceiptLedger()
    receipt = ledger.append({"k": 0})
    corrupted = dataclasses.replace(receipt, event_canonical_bytes=b'{"k":1}')
    assert not verify_chain((corrupted,))


def test_receipt_digest_corruption_is_detected():
    ledger = ReceiptLedger()
    receipt = ledger.append({"k": 0})
    corrupted = dataclasses.replace(receipt, receipt_digest="f" * 64)
    assert not verify_chain((corrupted,))


def test_malformed_receipt_fails_closed_without_raising():
    assert not verify_chain((object(),))


def test_concurrent_appends_are_linearized_into_gapless_order():
    ledger = ReceiptLedger()
    errors: list[BaseException] = []

    def worker(number: int) -> None:
        try:
            ledger.append({"worker": number})
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    snapshot = ledger.snapshot()
    assert not errors
    assert len(snapshot) == 50
    assert [r.seq for r in snapshot] == list(range(50))
    assert verify_chain(snapshot)


def test_key_order_canonical_vector():
    left = _canonical_bytes({"b": 1, "a": 2})
    right = _canonical_bytes({"a": 2, "b": 1})
    assert left == right == b'{"a":2,"b":1}'


def test_unicode_canonical_vector():
    assert _canonical_bytes({"n": "café"}) == '{"n":"café"}'.encode("utf-8")


def test_profile_is_bound_into_receipt_digest():
    receipt = ReceiptLedger().append({"k": 0})
    assert receipt.canon_profile == CANON_PROFILE
    assert receipt.core()["canon_profile"] == CANON_PROFILE


def test_origin_caller_cannot_assert_witness_binding():
    ledger = ReceiptLedger()
    with pytest.raises(TypeError):
        ledger.append({"k": 0}, witness_identity_binding="self-asserted")
    assert ledger.length() == 0


def test_origin_receipt_is_not_r3_eligible_by_default():
    receipt = ReceiptLedger().append({"k": 0})
    assert receipt.witness_identity_binding is None


def test_verifier_rejects_unverified_non_null_witness_metadata():
    receipt = ReceiptLedger().append({"k": 0})
    forged = Receipt(
        seq=receipt.seq,
        predecessor_digest=receipt.predecessor_digest,
        event_canonical_bytes=receipt.event_canonical_bytes,
        event_canonical_sha256=receipt.event_canonical_sha256,
        receipt_digest=receipt.receipt_digest,
        witness_identity_binding=None,
    )
    assert verify_chain((forged,))
