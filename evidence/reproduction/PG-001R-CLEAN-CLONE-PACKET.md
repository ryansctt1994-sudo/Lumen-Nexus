# PG-001R Clean-Clone Reproduction Packet

**Packet ID:** LNX-PG001R-REPRO-2026-09-28  
**Artifact:** PG-001R  
**Target issues:** #11 (first independent run), #12 (second independent run)  
**Authority:** NONE  
**Does not establish:** E4, R4, historical identity with PG-001, production authority

An origin-controlled clone is not an independent reproduction. This packet exists so a *different operator on non-origin hardware* can execute the same commands.

## Frozen identity

| Field | Value |
|---|---|
| Implementation commit | `aa52a1c854fa3d63a91c9c74a76ad2d1571197d9` |
| Repository | `https://github.com/ryansctt1994-sudo/Lumen-Nexus` |
| Source manifest | `evidence/manifests/pg-001r-source-manifest.json` |
| Historical equivalence | `false` |
| Evidence ceiling of this packet | at most `R2[self]` until a qualifying independent receipt exists |
| Authority | `NONE` |

Do not reproduce from the documentation branch that carries this packet. Reproduce from the implementation commit above.

## Preconditions

- Operator is not the origin implementer, or else the result must be labeled `ORIGIN_RERUN`, not independent.
- Hardware is not the origin workstation, or else the result must be labeled `ORIGIN_RERUN`.
- Network is used only to clone the repository. After checkout, tests must run offline.
- Python 3.11, 3.12, or 3.13. Standard library only. No extra packages.

## Commands

```bash
git clone https://github.com/ryansctt1994-sudo/Lumen-Nexus.git pg001r-repro
cd pg001r-repro
git checkout aa52a1c854fa3d63a91c9c74a76ad2d1571197d9
git rev-parse HEAD
python3 --version
uname -a
python3 tools/verify_pg001r_manifest.py
python3 -m unittest discover -s packages/verifier/tests -p 'test_pg001r.py' -v
```

Optional supplementary check (not part of the canonical 19):

```bash
python3 -m unittest discover -s tools/tests -p 'test_verify_pg001r_manifest.py' -v
```

## Expected results

Manifest verifier stdout must include:

```
PG-001R manifest verification PASSED
files verified: 10
conformance tests declared and discovered: 19
historical equivalence: false
evidence ceiling: R2[self]
authority: NONE
```

Exit code `0`.

Conformance suite must report:

```
Ran 19 tests ... OK
```

Exit code `0`.

Any other result is `FAILED_TO_REPRODUCE` or `INVALID_PACKAGE`. Do not repair the environment silently and then call the run independent.

## Outcome labels

Use exactly one:

- `REPRODUCED` — clean clone at the pinned commit, both commands exited 0, expected text present.
- `PARTIALLY_REPRODUCED` — package valid, at least one required command failed.
- `FAILED_TO_REPRODUCE` — package valid, material expected results absent.
- `INVALID_PACKAGE` — commit missing, manifest missing, or instructions insufficient.
- `ORIGIN_RERUN` — executed by origin operator or on origin hardware.

`ORIGIN_RERUN` cannot close #11 or #12.

## Required receipt fields

Copy `PG-001R-REPRODUCTION-RECEIPT.template.json` and fill:

- operator identity and relationship to origin team
- independence declaration
- hardware / OS / arch / Python version
- network policy after clone
- exact commit reproduced
- command transcript hashes or attached logs
- manifest exit code and test result
- outcome label
- statement that PG-001R is not PG-001

Signing profile is not yet accepted. Until #13 lands, the receipt is an unsigned structured record, not an R3/R4 credential.

## Non-claims

This packet does not:

- close #11 or #12 by existing;
- convert an origin re-run into independent evidence;
- transfer PG-001 historical receipts;
- raise evidence above R2[self];
- grant production authority.
