# Evidence Ladder

Promotion is a proof obligation. A repository setting, steward assertion, or passing CI run cannot override missing evidence.

`PromotionLevel = max { R | ProofObligation(R) is satisfied }`

| Level | Name | Minimum proof obligation | Authority ceiling |
|---|---|---|---|
| R0 | Concept | Identifiable idea or proposal | No execution authority |
| R1 | Specification | Written, reviewable specification with explicit claims and boundaries | Specification discussion only |
| R2 | Implemented and self-tested | Inspectable implementation plus origin-controlled tests | Prototype use under origin control |
| R3 | Cryptographically receipted execution | Reproducible local execution bound to canonical hashes and a valid origin receipt | Local verified claim only |
| R4 | Independent reproduction | Two valid receipts from distinct screened witnesses on non-origin hardware | Independently reproduced claim |
| R5 | Independent reimplementation | Implementation produced from the specification by an independent party and shown equivalent under the defined challenge suite | Reimplementation evidence; no automatic production approval |
| R6 | Production-authorized | Sustained operational evidence, applicable safety/regulatory gates, accountable human authority, rollback and incident controls | Explicitly scoped production authority |

## Global rules

1. Evidence is monotonic: required evidence must not silently decrease for the same capability and consequence.
2. Verified evidence must be a subset of recorded evidence.
3. Authority must not exceed verified evidence.
4. Origin-controlled repetition does not become independent reproduction by quantity.
5. Cryptographic integrity proves binding and tamper evidence; it does not prove semantic truth or witness independence.
6. Promotion is scoped to an immutable artifact, environment, challenge set, governance bundle, and authority domain.
7. Any material TCB or dependency change triggers replay or demotion as defined by the certificate lifecycle.

## Current ceiling

The ecosystem is recorded at R2[self], with submitted local component claims at R3[self]. No component in this repository is recorded above R3.