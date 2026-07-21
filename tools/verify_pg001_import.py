#!/usr/bin/env python3
"""Validate completeness and file integrity of a proposed PG-001 import.

This tool does not establish witness independence, semantic correctness,
signature validity, evidence promotion, seal release, or production authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_ROOTS = {"archive", "legacy", "research"}
ALLOWED_TOP_LEVELS = {"packages", "evidence", "tests", "tools"}
REQUIRED_TOP_LEVEL_KEYS = {
    "manifest_version",
    "artifact_id",
    "status",
    "claimed_evidence",
    "authority",
    "canonicalization_profile",
    "governance_bundle_sha256",
    "source",
    "tests",
    "receipt",
    "toolchain",
}


class AdmissionError(ValueError):
    """Raised when a proposed import violates the admission contract."""


@dataclass(frozen=True)
class FileRecord:
    role: str
    path: str
    sha256: str
    size_bytes: int


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def _require_exact_keys(obj: dict[str, Any], required: set[str], context: str) -> None:
    missing = sorted(required - set(obj))
    extra = sorted(set(obj) - required)
    _require(not missing, f"{context}: missing keys: {', '.join(missing)}")
    _require(not extra, f"{context}: unsupported keys: {', '.join(extra)}")


def _validate_sha256(value: Any, context: str) -> str:
    _require(isinstance(value, str), f"{context}: sha256 must be a string")
    _require(
        bool(SHA256_RE.fullmatch(value)),
        f"{context}: sha256 must be 64 lowercase hex characters",
    )
    return value


def _validate_relative_path(value: Any, context: str) -> str:
    _require(
        isinstance(value, str) and value,
        f"{context}: path must be a non-empty string",
    )
    _require("\\" not in value, f"{context}: path must use POSIX separators")
    path = PurePosixPath(value)
    _require(not path.is_absolute(), f"{context}: absolute paths are prohibited")
    _require(
        ".." not in path.parts and "." not in path.parts,
        f"{context}: traversal segments are prohibited",
    )
    _require(
        path.parts[0] in ALLOWED_TOP_LEVELS,
        f"{context}: path must begin in an admitted repository domain",
    )
    _require(
        path.parts[0] not in FORBIDDEN_ROOTS,
        f"{context}: quarantined domains are prohibited",
    )
    return value


def _parse_file_record(value: Any, role: str, index: int) -> FileRecord:
    context = f"{role}[{index}]"
    _require(isinstance(value, dict), f"{context}: record must be an object")
    _require_exact_keys(value, {"path", "sha256", "size_bytes"}, context)
    path = _validate_relative_path(value["path"], context)
    digest = _validate_sha256(value["sha256"], context)
    size = value["size_bytes"]
    _require(
        isinstance(size, int) and not isinstance(size, bool) and size >= 0,
        f"{context}: size_bytes must be a non-negative integer",
    )
    return FileRecord(role=role, path=path, sha256=digest, size_bytes=size)


def _parse_file_records(values: Any, role: str) -> list[FileRecord]:
    _require(
        isinstance(values, list) and values,
        f"{role}: at least one file record is required",
    )
    return [
        _parse_file_record(value, role, index)
        for index, value in enumerate(values)
    ]


def _iter_all_records(manifest: dict[str, Any]) -> Iterable[FileRecord]:
    yield from _parse_file_records(manifest["source"]["files"], "source.files")
    yield from _parse_file_records(manifest["tests"]["files"], "tests.files")
    yield _parse_file_record(manifest["receipt"]["file"], "receipt.file", 0)
    yield _parse_file_record(manifest["toolchain"]["lockfile"], "toolchain.lockfile", 0)


def validate_manifest(manifest: Any, repository_root: Path) -> list[FileRecord]:
    _require(isinstance(manifest, dict), "manifest: top-level value must be an object")
    _require_exact_keys(manifest, REQUIRED_TOP_LEVEL_KEYS, "manifest")

    _require(manifest["manifest_version"] == "1.0", "manifest_version: expected '1.0'")
    _require(manifest["artifact_id"] == "PG-001", "artifact_id: expected 'PG-001'")
    _require(
        manifest["status"] == "IMPORT_CANDIDATE",
        "status: expected 'IMPORT_CANDIDATE'",
    )
    _require(
        manifest["claimed_evidence"] == "R3[self]",
        "claimed_evidence: import harness permits only R3[self]",
    )
    _require(manifest["authority"] == "NONE", "authority: expected 'NONE'")
    _require(
        isinstance(manifest["canonicalization_profile"], str)
        and manifest["canonicalization_profile"].strip()
        and "placeholder" not in manifest["canonicalization_profile"].lower(),
        "canonicalization_profile: a non-placeholder profile identifier is required",
    )
    _validate_sha256(
        manifest["governance_bundle_sha256"],
        "governance_bundle_sha256",
    )

    source = manifest["source"]
    _require(isinstance(source, dict), "source: must be an object")
    _require_exact_keys(
        source,
        {"origin", "commit_or_bundle_id", "files"},
        "source",
    )
    _require(
        isinstance(source["origin"], str) and source["origin"].strip(),
        "source.origin: required",
    )
    _require(
        isinstance(source["commit_or_bundle_id"], str)
        and source["commit_or_bundle_id"].strip()
        and "placeholder" not in source["commit_or_bundle_id"].lower(),
        "source.commit_or_bundle_id: non-placeholder identifier required",
    )

    tests = manifest["tests"]
    _require(isinstance(tests, dict), "tests: must be an object")
    _require_exact_keys(tests, {"expected_test_count", "runner", "files"}, "tests")
    _require(
        tests["expected_test_count"] == 19,
        "tests.expected_test_count: expected exactly 19",
    )
    _require(
        isinstance(tests["runner"], str) and tests["runner"].strip(),
        "tests.runner: required",
    )

    receipt = manifest["receipt"]
    _require(isinstance(receipt, dict), "receipt: must be an object")
    _require_exact_keys(
        receipt,
        {"file", "signature_algorithm", "signer_key_id", "reported_result"},
        "receipt",
    )
    _require(
        receipt["signature_algorithm"] == "Ed25519",
        "receipt.signature_algorithm: expected Ed25519",
    )
    _require(
        isinstance(receipt["signer_key_id"], str)
        and receipt["signer_key_id"].strip(),
        "receipt.signer_key_id: required",
    )
    _require(
        receipt["reported_result"] == "19/19 passed",
        "receipt.reported_result: expected '19/19 passed'",
    )

    toolchain = manifest["toolchain"]
    _require(isinstance(toolchain, dict), "toolchain: must be an object")
    _require_exact_keys(toolchain, {"python", "platform", "lockfile"}, "toolchain")
    _require(
        isinstance(toolchain["python"], str) and toolchain["python"].strip(),
        "toolchain.python: required",
    )
    _require(
        isinstance(toolchain["platform"], str) and toolchain["platform"].strip(),
        "toolchain.platform: required",
    )

    records = list(_iter_all_records(manifest))
    paths = [record.path for record in records]
    _require(len(paths) == len(set(paths)), "files: duplicate paths are prohibited")

    root = repository_root.resolve()
    for record in records:
        candidate = (root / record.path).resolve()
        _require(
            candidate.is_relative_to(root),
            f"{record.role}: resolved path escapes repository root",
        )
        _require(candidate.is_file(), f"{record.role}: missing file: {record.path}")
        actual_size = candidate.stat().st_size
        _require(
            actual_size == record.size_bytes,
            f"{record.role}: size mismatch for {record.path}",
        )
        actual_digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        _require(
            actual_digest == record.sha256,
            f"{record.role}: sha256 mismatch for {record.path}",
        )

    return records


def load_and_validate(manifest_path: Path, repository_root: Path) -> list[FileRecord]:
    _require(manifest_path.is_file(), f"manifest not found: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AdmissionError(f"manifest: invalid JSON: {exc}") from exc
    return validate_manifest(manifest, repository_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        nargs="?",
        default="evidence/pg-001/manifest.json",
        help="Path to the proposed PG-001 manifest",
    )
    parser.add_argument(
        "--repository-root",
        default=".",
        help="Repository root used to resolve manifest file records",
    )
    args = parser.parse_args(argv)

    try:
        records = load_and_validate(Path(args.manifest), Path(args.repository_root))
    except AdmissionError as exc:
        print(f"PG-001 ADMISSION REJECTED: {exc}", file=sys.stderr)
        return 2

    print(f"PG-001 IMPORT INTEGRITY VALIDATED: {len(records)} file records")
    print("NO EVIDENCE PROMOTION OR AUTHORITY GRANTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
