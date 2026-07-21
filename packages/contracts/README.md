# Contracts Trust Domain

This directory contains schemas, canonical data models, stable interfaces, and test vectors shared across Lumen Nexus components.

## Boundary

- Zero dependencies on `packages/runtime` or `packages/verifier`.
- No stateful execution, network calls, model invocation, signing-key access, or policy decisions.
- Canonicalization and schema changes are versioned and evidence-impacting.
- Backward-incompatible changes require explicit migration and replay analysis.

## Current implementation

`lumen_contracts/pg001r.py` defines the strict PG-001R promotion-request contract, evidence and authority enums, and the frozen authority/evidence floors.

The module validates structure and types only. It does not decide promotion or establish that supplied evidence assertions are true. PG-001R remains a clean-room artifact with an R2[self] ceiling after origin-controlled conformance testing and no production authority.
