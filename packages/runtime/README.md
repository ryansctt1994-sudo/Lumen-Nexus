# Runtime Trust Domain

This directory is reserved for stateful governed execution: request admission, policy evaluation, model access, chronicle append, witness interaction, and response delivery.

## Boundary

- May depend on `packages/contracts` only among project trust domains.
- Must not import `packages/verifier`.
- Must not import from `archive/`, `legacy/`, `research/`, or `evidence/`.
- Must fail closed when authority, evidence, policy, receipt, or ledger state is ambiguous.
- Must not expose output before required post-generation policy and receipt operations complete.

## Current state

No WeaverX runtime implementation is committed. This placeholder grants no runtime or production authority.