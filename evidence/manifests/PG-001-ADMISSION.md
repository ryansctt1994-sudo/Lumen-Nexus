# PG-001 Import Admission Contract

**Contradiction:** C-PR006-001  
**Tracking issue:** [#5](https://github.com/ryansctt1994-sudo/Lumen-Nexus/issues/5)  
**Current admission state:** NOT ADMITTED  
**Maximum accepted claim at import:** R3[self]  
**Authority:** NONE

This contract defines the minimum integrity envelope for importing the exact frozen PG-001 source, its documented 19-test suite, dependency anchors, and local receipt packet.

It does not reconstruct missing materials and does not convert integrity validation into independent reproduction.

## Required import location

A candidate import must provide:

```text
evidence/pg-001/manifest.json
```

The manifest must conform to `pg-001.manifest.schema.json` and every referenced file must exist in an admitted repository domain.

## Enforced properties

`tools/verify_pg001_import.py` rejects:

- abbreviated or non-lowercase SHA-256 values;
- missing, altered, or size-mismatched files;
- absolute paths, traversal paths, and Windows-style separators;
- files rooted outside `packages/`, `evidence/`, `tests/`, or `tools/`;
- duplicate file paths across source, tests, receipt, and lockfile records;
- any expected test count other than 19;
- evidence claims above `R3[self]`;
- any authority value other than `NONE`;
- placeholder source, bundle, or canonicalization identifiers;
- unsupported manifest fields that could silently expand semantics.

## Deliberately not established

A successful integrity run does not establish:

- that the imported source is historically identical to the undocumented local source;
- that the 19 tests are adequate or semantically complete;
- that the reported test result is truthful;
- that the Ed25519 signature is valid;
- that the signer is independent;
- that the canonicalization profile is correctly implemented;
- that PG-001 satisfies R4 or any production gate;
- that C-PR006-001 is closed.

Those obligations require separate verification, receipt validation, clean-clone execution, registry disposition, and an explicit gate decision.

## Validation command

After the exact candidate files and manifest are committed:

```bash
python tools/verify_pg001_import.py evidence/pg-001/manifest.json --repository-root .
```

The verifier exits non-zero on any contract or integrity failure. Success prints both an integrity result and an explicit statement that no evidence promotion or authority is granted.

## CI transition

The current workflow tests the admission harness itself. It does not run the verifier against a real PG-001 manifest because no such manifest is committed.

When the exact materials are available, the import pull request must add a CI step that executes the validation command above. That change must not be merged if the manifest or any referenced file is missing.
