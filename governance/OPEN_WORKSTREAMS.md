# Open Governance Workstreams

**Effective date:** 2026-07-21  
**Default posture:** FAIL CLOSED  
**Promotion:** BLOCKED  
**Seal:** HELD  
**Production authority:** NONE — PROHIBITED

This index links the machine-readable contradiction registry to the operational GitHub work queue. GitHub issue state is not authoritative by itself: `governance/CONTRADICTIONS.yaml`, committed repair evidence, and an explicit gate decision determine disposition.

## Critical path

| Priority | Contradiction | GitHub issue | Required outcome | Current status |
|---|---|---|---|---|
| P0 | C-RCPT-001 | [#3](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/3) | Single-owner `ReceiptLedger`, adversarial tests, reproducible repair receipt, gate decision | OPEN |
| P0 | C-EVID-001 | [#4](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/4) | Bind, downgrade, or preserve every audit claim; prove unsupported claims fail closed | OPEN |
| P0 | C-PR006-001 | [#5](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/5) | Import exact PG-001 source, 19 tests, full hashes, receipt packet, clean-clone reproduction | OPEN |
| P1 | C-ANCHOR-001 | [#7](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/7) | Complete immutable build-anchor manifest and clean-clone verification | OPEN |
| P1 | C-DUAL-001 | [#6](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/6) | Enforceable dual-steward approval protocol with negative test | OPEN |

## Execution order

1. Acquire and inventory the exact PG-001 materials without reconstruction.
2. Resolve receipt-chain ownership under ADR-0006 and produce the repair evidence.
3. Reconcile the evidence-audit claim surface against committed receipts.
4. Replace abbreviated and placeholder anchors with complete immutable identifiers.
5. Establish enforceable dual-steward authorization.
6. Assemble the E4 replication bundle only after the applicable preconditions are satisfied.

The first three workstreams may proceed in parallel when their source artifacts are available. None may silently consume reconstructed, renamed, or semantically altered inputs as though they were the frozen originals.

## Closure protocol

A workstream is not closed merely because its GitHub issue is closed. Closure requires:

- the contradiction registry to record the disposition;
- exact source and artifact identifiers;
- positive and negative tests;
- reproducible commands and environment anchors;
- the applicable repair or reproduction receipt;
- an explicit gate decision;
- confirmation that authority remains within the resulting evidence ceiling.

Any mismatch between the issue tracker and the registry resolves to the stricter, lower-authority state.
