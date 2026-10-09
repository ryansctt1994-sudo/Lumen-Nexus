# ADR-0006: Single-Owner ReceiptLedger

- **Status:** CANDIDATE IMPLEMENTATION — NOT ACCEPTED
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
7. immutable canonical-event retention;
8. read-only snapshots for verifiers.

Callers provide logical event content. They do not provide or mutate predecessor hashes, sequence values, ledger heads, witness identity claims, or committed receipt objects.

## Required invariants

- Exactly one component owns mutable linkage state.
- The canonical event bytes retained in the receipt are the exact bytes hashed.
- Failed appends do not advance sequence or chain head.
- Returned objects cannot mutate stored state.
- Concurrent successful appends are linearized into one unambiguous gapless committed order, or fail explicitly. This does not claim reproducible thread-scheduling order across runs.
- Sequential replay reconstructs the same chain from the same logical event sequence and canonicalization profile.
- Verification remains read-only and cannot latch, execute, or repair the ledger.
- Origin callers cannot self-assert witness identity binding. Witness evidence belongs to a separately specified and verified receipt envelope.

## Required evidence before acceptance

- positive append and replay tests;
- predecessor, sequence, and canonicalization mismatch rejection tests;
- mutation-isolation tests on ingress, storage, and return paths;
- canonical-event corruption detection;
- concurrency and interrupted-transaction tests;
- cross-runtime canonicalization vectors;
- witness-boundary rejection tests;
- a clean-clone repair receipt bound to full source and environment hashes.

## Consequences

This decision removes dual ownership but centralizes a critical state boundary. The ledger therefore becomes part of the trusted computing base and requires explicit persistence, recovery, concurrency, serialization, and key-rotation specifications.

Retaining canonical event bytes permits direct verification of event-to-receipt correspondence but increases storage requirements. External content-addressed retention may be introduced later only through a separate accepted profile that defines availability and integrity guarantees.

## Candidate implementation

A candidate implementation and conformance suite are present under:

- `packages/runtime/lumen_runtime/receipt_ledger.py`
- `packages/runtime/tests/test_receipt_ledger.py`

Their presence and passing tests do not close `C-RCPT-001`, raise the ecosystem evidence ceiling, establish witness independence, or grant authority.

## Current outcome

`C-RCPT-001` remains OPEN. Acceptance still requires steward disposition, a clean-clone repair receipt, and an explicit gate decision. This ADR and its candidate implementation must not be cited as evidence that the historical defect is repaired.
