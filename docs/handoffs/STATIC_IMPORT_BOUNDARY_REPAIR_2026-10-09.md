# Static import-boundary repair — candidate

Source base: PR #29, `f3088ebd03c24e0be55338e676a7894a2bfb18fa`.

The checker inspected only the module portion of a from-import. Consequently,
`from packages import runtime` and its aliased form escaped the verifier's
runtime-import prohibition. The old relative-level threshold also admitted
some shallow escapes while incorrectly rejecting deeper imports that stayed
inside the same trust domain.

The checker now includes each imported name in the qualified target and resolves
relative imports against the source file's containing package. Relative targets
outside that file's trust domain are refused. A wildcard import from the project
root is ambiguous and refused. Absolute contracts imports, standard-library
imports, and valid within-domain relative imports remain allowed.

`tools/tests/test_check_boundaries.py` exercises positive and negative controls.
The existing Trust Boundaries workflow now runs this unittest suite without
adding third-party test dependencies.

Local Python 3.12 results, 2026-10-09:

- Original checker: 9 unittest failures, including subtest failures, across
  the 9-method boundary suite.
- Repaired checker: all 9 methods pass.
- Full repository pytest: 91 passed, 17 subtests passed.
- Real repository boundary check and frozen PG-001R source manifest: PASS.

Reproduce with `python -m unittest tools.tests.test_check_boundaries -v`.
Use the new test file with the exact base checker to reproduce the failures.

This remains a static syntax check. It does not sandbox Python, trace dynamic
imports or attribute access, authenticate installed packages, or prove runtime
dependency isolation. No contradiction is automatically closed, historical
manifest changed, witness admitted, or production authority granted.
