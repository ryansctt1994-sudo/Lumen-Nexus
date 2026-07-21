from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_pg001r_manifest.py"
SPEC = importlib.util.spec_from_file_location("verify_pg001r_manifest", MODULE_PATH)
assert SPEC and SPEC.loader
verify = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verify
SPEC.loader.exec_module(verify)


class PG001RManifestVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.files: dict[str, bytes] = {}
        for path in sorted(str(item) for item in verify.EXPECTED_PATHS):
            content = b"content:" + path.encode("utf-8") + b"\n"
            self.files[path] = content
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

        test_path = self.root / "packages/verifier/tests/test_pg001r.py"
        test_path.write_text(
            "import unittest\n\nclass T(unittest.TestCase):\n"
            + "".join(
                f"    def test_{index:02d}(self):\n        pass\n"
                for index in range(1, 20)
            ),
            encoding="utf-8",
        )
        self.files["packages/verifier/tests/test_pg001r.py"] = test_path.read_bytes()
        self.manifest = self._manifest()
        manifest_path = self.root / "evidence/manifests/pg-001r-source-manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.manifest_path = manifest_path

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _manifest(self) -> dict[str, object]:
        records = []
        for path in sorted(self.files):
            content = self.files[path]
            records.append(
                {
                    "path": path,
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "size_bytes": len(content),
                }
            )
        return {
            "manifest_version": "1.0",
            "artifact_id": "PG-001R",
            "source_identity": "clean-room-reimplementation",
            "historical_equivalence": False,
            "evidence_ceiling": "R2[self]",
            "authority": "NONE",
            "expected_conformance_tests": 19,
            "files": records,
        }

    def run_verifier(self) -> int:
        with patch.object(verify, "ROOT", self.root), patch.object(
            verify, "MANIFEST", self.manifest_path
        ):
            return verify.main()

    def rewrite_manifest(self) -> None:
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_valid_manifest_passes(self) -> None:
        self.assertEqual(0, self.run_verifier())

    def test_missing_required_file_record_fails(self) -> None:
        self.manifest["files"].pop()
        self.rewrite_manifest()
        self.assertEqual(1, self.run_verifier())

    def test_unexpected_file_record_fails(self) -> None:
        self.manifest["files"].append(
            {"path": "tools/extra.txt", "sha256": "0" * 64, "size_bytes": 0}
        )
        self.rewrite_manifest()
        self.assertEqual(1, self.run_verifier())

    def test_windows_style_path_fails(self) -> None:
        self.manifest["files"][0]["path"] = "..\\escape.txt"
        self.rewrite_manifest()
        self.assertEqual(1, self.run_verifier())

    def test_hash_mismatch_fails(self) -> None:
        self.manifest["files"][0]["sha256"] = "0" * 64
        self.rewrite_manifest()
        self.assertEqual(1, self.run_verifier())

    def test_test_count_inflation_fails(self) -> None:
        self.manifest["expected_conformance_tests"] = 20
        self.rewrite_manifest()
        self.assertEqual(1, self.run_verifier())

    def test_historical_equivalence_claim_fails(self) -> None:
        self.manifest["historical_equivalence"] = True
        self.rewrite_manifest()
        self.assertEqual(1, self.run_verifier())

    def test_evidence_inflation_fails(self) -> None:
        self.manifest["evidence_ceiling"] = "R3[self]"
        self.rewrite_manifest()
        self.assertEqual(1, self.run_verifier())

    def test_authority_claim_fails(self) -> None:
        self.manifest["authority"] = "PRODUCTION"
        self.rewrite_manifest()
        self.assertEqual(1, self.run_verifier())


if __name__ == "__main__":
    unittest.main()
