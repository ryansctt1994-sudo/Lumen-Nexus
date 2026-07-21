# Verifier Trust Domain

This directory is reserved for read-only verification of contracts, receipts, certificates, chains, canonical bytes, signatures, replay results, and promotion eligibility.

## Boundary

- May depend on `packages/contracts` only among project trust domains.
- Must not import or execute `packages/runtime`.
- Must not mutate ledger state, issue operational authority, repair artifacts, invoke models, or latch the host system.
- Verification failure returns a deterministic negative result; it does not silently downgrade requirements or create replacement evidence.

## Current implementation

`lumen_verifier/pg001r.py` implements PG-001R, a clean-room promotion-gate evaluator. It enforces the seven frozen blocker classes plus the required/verified/recorded evidence subset invariants and returns every applicable blocker in deterministic order.

The evaluator reports promotion and authority eligibility only. It does not verify upstream evidence truth, issue a governance receipt, close contradictions, establish historical identity with PG-001, or grant production authority.

The canonical suite is `tests/test_pg001r.py` with exactly 19 conformance tests. Origin-controlled success establishes at most R2[self].
