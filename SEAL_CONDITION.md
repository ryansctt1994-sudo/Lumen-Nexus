# Seal Condition

**State:** HELD  
**Effective date:** 2026-07-21  
**Automatic release:** DISABLED  
**Production authority:** NONE — PROHIBITED

The seal records that the architecture is frozen while promotion authority is withheld. It is not a cryptographic signature, a production approval, or a claim of independent verification.

## Release prerequisites

The seal must remain held while any seal-blocking contradiction is open, witness independence is unverified, or the applicable repair receipt cannot be reproduced from a clean clone.

At minimum, a proposed release transition requires:

1. a repair receipt conforming to the frozen canonicalization and signing profile;
2. disposition of each applicable blocker in `governance/CONTRADICTIONS.yaml`;
3. an auditable gate decision referencing immutable artifact identifiers;
4. confirmation that no authority exceeds the verified evidence ceiling;
5. dual-steward authorization after `C-DUAL-001` is technically resolved.

## Baseline ambiguity

The handoff contains both a reference to release after the first valid repair receipt and a stricter requirement that all open contradictions be dispositioned before release. The repository adopts the stricter fail-closed interpretation. No workflow may automatically change this file to `RELEASED`.

## Current result

**SEAL HELD. PROMOTION WITHHELD. PRODUCTION AUTHORITY NONE — PROHIBITED.**