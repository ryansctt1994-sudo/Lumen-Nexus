# Receipt intake repair — review candidate

Base: PR #29, `8f744f5b98242e4509ac0af97d1dc7b8de448ad4`.

The old verifier accepted correctly rehashed receipts containing arbitrary
non-JSON bytes, duplicate object names, noncanonical JSON, NaN/Infinity, invalid
UTF-8, or UTF-16. It also accepted rehashed boolean/float sequence values and
mutable bytearrays. Append silently converted non-string object names.

The repair requires immutable UTF-8 canonical event bytes, exact integer
sequences, and string object names. It retains ordinary JSON encodings and
hashes; no historical PG-001R source or manifest was changed.

Local Python 3.12 validation on 2026-10-09:

- New tests against the base implementation: **17 failed, 25 passed**.
- Repaired ledger suite: **42 passed**.
- All discovered repository tests: **82 passed**.
- Trust-boundary checker and frozen PG-001R source-manifest verifier: PASS.

Reproduce with `python -m pytest -q`; to reproduce RED, use the changed test
file against the exact base implementation. The tests rehash adversarial
records so rejection cannot be attributed merely to a stale digest.

This is assistant-managed local execution, not independent reproduction or
witness admission. Hosted CI is a separate check. C-RCPT-001 remains open;
candidate status, R2[self], authority NONE, and production restrictions remain.
The ledger remains in-memory; persistence, crash atomicity, resource exhaustion,
and active mutation by the caller during append are outside this repair.
