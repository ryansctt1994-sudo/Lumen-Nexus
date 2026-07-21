from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_pg001_import.py"
SPEC = importlib.util.spec_from_file_location("verify_pg001_import", MODULE_PATH)
assert SPEC and SPEC.loader
verify = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verify
SPEC.loader.exec_module(verify)


class PG001AdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.records = {
            "packages/runtime/pg001.py": b"def gate():\n    return False\n",
            "tests/test_pg001.py": b"def test_gate():\n    assert True\n",
            "evidence/receipts/pg001.json": b'{"result":"19/19 passed"}\n',
            "evidence/locks/pg001.lock": b"python==3.12.4\n",
        }
        for path, content in self.records.items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        self.manifest = self._valid_manifest()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _record(self, path: str) -> dict[str, object]:
        content = self.records[path]
        return {
            "path": path,
            "sha256": hashlib.sha256(content).hexdigest(),
            "size_bytes": len(content),
        }

    def _valid_manifest(self) -> dict[str, object]:
        return {
            "manifest_version": "1.0",
            "artifact_id": "PG-001",
            "status": "IMPORT_CANDIDATE",
            "claimed_evidence": "R3[self]",
            "authority": "NONE",
            "canonicalization_profile": "triweavon-cjson-v1",
            "governance_bundle_sha256": "a" * 64,
            "source": {
                "origin": "frozen local bundle",
                "commit_or_bundle_id": "bundle-2026-07-21",
                "files": [self._record("packages/runtime/pg001.py")],
            },
            "tests": {
                "expected_test_count": 19,
                "runner": "python -m pytest tests/test_pg001.py",
                "files": [self._record("tests/test_pg001.py")],
            },
            "receipt": {
                "file": self._record("evidence/receipts/pg001.json"),
                "signature_algorithm": "Ed25519",
                "signer_key_id": "origin-key-01",
                "reported_result": "19/19 passed",
            },
            "toolchain": {
                "python": "3.12.4",
                "platform": "linux-x86_64",
                "lockfile": self._record("evidence/locks/pg001.lock"),
            },
        }

    def assert_rejected(self, fragment: str) -> None:
        with self.assertRaisesRegex(verify.AdmissionError, fragment):
            verify.validate_manifest(self.manifest, self.root)

    def test_valid_manifest_passes_integrity_validation(self) -> None:
        records = verify.validate_manifest(self.manifest, self.root)
        self.assertEqual(4, len(records))

    def test_abbreviated_hash_is_rejected(self) -> None:
        self.manifest["governance_bundle_sha256"] = "abcd"
        self.assert_rejected("64 lowercase hex")

    def test_hash_mismatch_is_rejected(self) -> None:
        self.manifest["source"]["files"][0]["sha256"] = "b" * 64
        self.assert_rejected("sha256 mismatch")

    def test_size_mismatch_is_rejected(self) -> None:
        self.manifest["source"]["files"][0]["size_bytes"] = 999
        self.assert_rejected("size mismatch")

    def test_path_traversal_is_rejected(self) -> None:
        self.manifest["source"]["files"][0]["path"] = "../pg001.py"
        self.assert_rejected("traversal")

    def test_duplicate_paths_are_rejected(self) -> None:
        self.manifest["tests"]["files"][0] = dict(
            self.manifest["source"]["files"][0]
        )
        self.assert_rejected("duplicate paths")

    def test_wrong_test_count_is_rejected(self) -> None:
        self.manifest["tests"]["expected_test_count"] = 18
        self.assert_rejected("exactly 19")

    def test_inflated_evidence_claim_is_rejected(self) -> None:
        self.manifest["claimed_evidence"] = "R4"
        self.assert_rejected(r"permits only R3\[self\]")

    def test_authority_claim_is_rejected(self) -> None:
        self.manifest["authority"] = "PRODUCTION"
        self.assert_rejected("expected 'NONE'")

    def test_missing_file_is_rejected(self) -> None:
        (self.root / "packages/runtime/pg001.py").unlink()
        self.assert_rejected("missing file")

    def test_placeholder_identifier_is_rejected(self) -> None:
        self.manifest["source"]["commit_or_bundle_id"] = "PLACEHOLDER"
        self.assert_rejected("non-placeholder")

    def test_extra_keys_are_rejected(self) -> None:
        self.manifest["self_certified"] = True
        self.assert_rejected("unsupported keys")


if __name__ == "__main__":
    unittest.main()
