# Verifier Trust Domain

This directory is reserved for read-only verification of contracts, receipts, certificates, chains, canonical bytes, signatures, and replay results.

## Boundary

- May depend on `packages/contracts` only among project trust domains.
- Must not import or execute `packages/runtime`.
- Must not mutate ledger state, issue authority, repair artifacts, invoke models, or latch the host system.
- Verification failure returns a deterministic negative result; it does not silently downgrade requirements or create replacement evidence.

## Current state

No verifier implementation is committed. This placeholder does not substantiate the submitted Omega Provenance or WeaverX verifier claims.