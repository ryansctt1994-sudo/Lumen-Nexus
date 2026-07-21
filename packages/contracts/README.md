# Contracts Trust Domain

This directory contains schemas, canonical data models, stable interfaces, and test vectors shared across Lumen Nexus components.

## Boundary

- Zero dependencies on `packages/runtime` or `packages/verifier`.
- No stateful execution, network calls, model invocation, signing-key access, or policy decisions.
- Canonicalization and schema changes are versioned and evidence-impacting.
- Backward-incompatible changes require explicit migration and replay analysis.

## Current state

No production contracts are committed. This placeholder establishes the trust boundary only and does not satisfy any implementation or evidence obligation.