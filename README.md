# Lumen Nexus

Governed, evidence-first architecture for trustworthy AI systems and its flagship governed inference runtime, WeaverX.

> The Nexus does not trust—it proves.

## Current posture

- Architecture: **FROZEN**
- Promotion: **HOLD**
- Seal: **HELD**
- Ecosystem evidence ceiling: **R2[self]**, with documented local component pockets at R3[self]
- Production authority: **NONE — PROHIBITED**

Repository presence, documentation, CI success, or configuration values do not promote an artifact's evidence level.

## Start here

- [Professional handoff v2.0](docs/handoffs/LNX-HANDOFF-2026-07-21-v2.0.md)
- [Repository status](STATUS.md)
- [Authority boundary](AUTHORITY.md)
- [Seal condition](SEAL_CONDITION.md)
- [Evidence ladder](governance/EVIDENCE_LADDER.md)
- [Open contradictions](governance/CONTRADICTIONS.yaml)
- [ADR-0006 receipt-chain repair](governance/adr/ADR-0006-receipt-ledger.md)

## Trust domains

```text
packages/contracts   # schemas and stable interfaces; zero project dependencies
packages/runtime     # stateful execution; may depend on contracts only
packages/verifier    # read-only verification; may depend on contracts only
```

`archive/`, `legacy/quarantine/`, `research/`, and `evidence/` are non-runtime domains. The CI boundary checker rejects prohibited imports and missing governance controls.

## Deliberately absent

This repository skeleton does **not** yet contain the frozen WeaverX baseline, PG-001 source and tests, repair receipts, independent witness receipts, or an E4 reproduction bundle. Their absence remains evidence-bearing and must not be concealed by placeholders.

## Use restrictions

No production, clinical, legal, financial, emergency, autonomous high-stakes, hardware-verification, formal-proof, or AGI-safety authority is granted by this repository.