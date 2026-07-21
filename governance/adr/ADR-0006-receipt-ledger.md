# ADR-0006: Single-Owner ReceiptLedger

- **Status:** PROPOSED — NOT IMPLEMENTED
- **Date:** 2026-07-21
- **Decision authority:** WITHHELD pending steward approval and executable evidence
- **Related contradiction:** C-RCPT-001

## Context

The submitted baseline reports incompatible linkage semantics between `receipt.py` and `hashchain.py`, including caller-owned chain state. Multiple components must not independently decide predecessor linkage because that permits divergent chains, duplicated ownership, and receipts that appear internally valid while binding different histories.

## Proposed decision

Introduce one state-owning `ReceiptLedger` boundary responsible for:

1. canonical event admission;
2. predecessor selection;
3. monotonic sequence assignment;
4. atomic append;
5. chain-head persistence;
6. receipt materialization after successful commit;
7. read-only snapshots for verifiers.

Callers provide logical event content. They do not provide or mutate predecessor hashes, sequence values, ledger heads, or committed receipt objects.

## Required invariants

- Exactly one component owns mutable linkage state.
- The stored canonical event bytes are the bytes hashed and signed.
- Failed appends do not advance sequence or chain head.
- Returned objects cannot mutate stored state.
- Concurrent appends have a deterministic total order or fail explicitly.
- Replay reconstructs the same chain from the same canonical event sequence.
- Verification remains read-only and cannot latch, execute, or repair the ledger.

## Required evidence before acceptance

- positive append and replay tests;
- predecessor, sequence, and canonicalization mismatch rejection tests;
- mutation-isolation tests on ingress, storage, and return paths;
- concurrency and interrupted-transaction tests;
- cross-runtime canonicalization vectors;
- a clean-clone repair receipt bound to full source and environment hashes.

## Consequences

This decision removes dual ownership but centralizes a critical state boundary. The ledger therefore becomes part of the trusted computing base and requires explicit persistence, recovery, concurrency, and key-rotation specifications.

## Current outcome

No implementation is present in this repository. `C-RCPT-001` remains OPEN, and this ADR must not be cited as evidence that the defect is repaired.