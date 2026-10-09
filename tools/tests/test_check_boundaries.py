"""Executable regression tests for static trust-domain import admission."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tools import check_boundaries as checker


class BoundaryImportTests(unittest.TestCase):
    def inspect(self, source, domain="verifier", relative_path=None):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / (relative_path or f"packages/{domain}/example.py")
            path.parent.mkdir(parents=True)
            path.write_text(source, encoding="utf-8")
            with patch.object(checker, "ROOT", root):
                return checker.check_domain(domain)

    def test_from_import_alias_cannot_hide_forbidden_domain(self):
        for domain, source in (
            ("verifier", "from packages import runtime"),
            ("verifier", "from packages import runtime as innocent"),
            ("runtime", "from packages import verifier"),
            ("contracts", "from packages import runtime"),
            ("contracts", "from packages import verifier"),
        ):
            with self.subTest(domain=domain, source=source):
                violations = self.inspect(source, domain)
                self.assertTrue(any(v.rule == "trust-domain-import" for v in violations))

    def test_relative_parent_alias_cannot_escape_domain(self):
        violations = self.inspect("from .. import runtime")
        self.assertTrue(any(v.rule == "relative-import" for v in violations))

    def test_relative_named_parent_cannot_escape_domain(self):
        violations = self.inspect("from ..runtime import api")
        self.assertTrue(any(v.rule == "relative-import" for v in violations))

    def test_project_root_star_import_is_ambiguous(self):
        violations = self.inspect("from packages import *")
        self.assertTrue(any(v.rule == "ambiguous-import" for v in violations))

    def test_deep_relative_import_can_remain_inside_domain(self):
        violations = self.inspect(
            "from ... import helpers", relative_path="packages/verifier/a/b/check.py"
        )
        self.assertEqual(violations, [])

    def test_package_initializer_relative_import_stays_in_package(self):
        self.assertEqual(self.inspect(
            "from . import helper", relative_path="packages/verifier/a/__init__.py"
        ), [])

    def test_allowed_absolute_and_relative_imports_remain_allowed(self):
        for source in (
            "import json", "from pathlib import Path",
            "from packages import contracts", "from packages.contracts import model",
            "from . import helpers", "from .helpers import check",
            "import packages.verifier.helpers",
        ):
            with self.subTest(source=source):
                self.assertEqual(self.inspect(source), [])

    def test_direct_forbidden_imports_still_refused(self):
        for source in (
            "import packages.runtime.lumen_runtime",
            "from packages.runtime import lumen_runtime",
            "from lumen_runtime import api",
        ):
            with self.subTest(source=source):
                self.assertTrue(self.inspect(source))

    def test_quarantine_imports_still_refused(self):
        for source in ("from archive import sample", "import research.sample"):
            with self.subTest(source=source):
                self.assertTrue(any(v.rule == "quarantine-import" for v in self.inspect(source)))


if __name__ == "__main__":
    unittest.main()
