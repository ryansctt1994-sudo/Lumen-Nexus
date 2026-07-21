# Open Governance Workstreams

**Effective date:** 2026-07-21  
**Default posture:** FAIL CLOSED  
**Promotion:** BLOCKED  
**Seal:** HELD  
**Production authority:** NONE — PROHIBITED

This index links the machine-readable contradiction registry to the operational GitHub work queue. GitHub issue state is not authoritative by itself: `governance/CONTRADICTIONS.yaml`, committed repair evidence, and an explicit gate decision determine disposition.

## Contradiction critical path

| Priority | Contradiction | GitHub issue | Required outcome | Current status |
|---|---|---|---|---|
| P0 | C-RCPT-001 | [#3](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/3) | Single-owner `ReceiptLedger`, adversarial tests, reproducible repair receipt, gate decision | OPEN |
| P0 | C-EVID-001 | [#4](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/4) | Bind, downgrade, or preserve every audit claim; prove unsupported claims fail closed | OPEN |
| P0 | C-PR006-001 | [#5](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/5) | Recover exact PG-001 materials or explicitly disposition historical loss without transferring identity to PG-001R | OPEN |
| P1 | C-ANCHOR-001 | [#7](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/7) | Complete immutable build-anchor manifest and clean-clone verification | OPEN |
| P1 | C-DUAL-001 | [#6](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/6) | Enforceable dual-steward approval protocol with negative test | OPEN |

## PG-001R clean-room successor

PG-001R is a new artifact and does not inherit PG-001 identity or evidence.

| Priority | Workstream | GitHub issue | Required outcome | Current status |
|---|---|---|---|---|
| P0 | Reference implementation | [#10](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/10) | Frozen specification, strict contracts, read-only evaluator, 19 tests, source manifest, CI | COMPLETE — R2[self] |
| P1 | Receipt profile | [#13](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/13) | Approved canonical signed payload and independent verifier aligned with ADR-0006 | BLOCKED BY #3 |
| P1 | First reproduction | [#11](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/11) | Clean-clone non-origin reproduction and independence record | WAITING |
| P1 | Second reproduction | [#12](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/12) | Distinct second witness receipt for the R4 count | WAITING |
| P2 | Historical disposition | [#14](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/14) | Registry decision preserving the separation between PG-001 and PG-001R | WAITING |

The reference implementation is bound to merge commit `aa52a1c854fa3d63a91c9c74a76ad2d1571197d9`. Completion establishes origin-controlled implementation and self-test evidence only.

## Execution order

1. Resolve receipt-chain ownership under ADR-0006 and produce repair evidence.
2. Define the PG-001R receipt and gate-decision profile without creating a second linkage owner.
3. Reconcile the evidence-audit claim surface against committed receipts.
4. Obtain two independent PG-001R reproductions on non-origin hardware.
5. Disposition C-PR006-001 as exact recovery or explicit historical loss; never relabel PG-001R as PG-001.
6. Replace abbreviated and placeholder anchors with complete immutable identifiers.
7. Establish enforceable dual-steward authorization.
8. Assemble the E4 replication bundle only after the applicable preconditions are satisfied.

The receipt-chain, evidence-audit, and independent-reproduction preparations may proceed in parallel where their dependencies permit. None may silently consume reconstructed, renamed, or semantically altered inputs as though they were frozen originals.

## Closure protocol

A workstream is not closed merely because its GitHub issue is closed. Closure requires:

- the contradiction or artifact registry to record the disposition;
- exact source and artifact identifiers;
- positive and negative tests;
- reproducible commands and environment anchors;
- the applicable repair or reproduction receipt;
- an explicit gate decision;
- confirmation that authority remains within the resulting evidence ceiling.

Any mismatch between the issue tracker and the registry resolves to the stricter, lower-authority state.
