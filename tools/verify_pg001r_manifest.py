"""Verify the PG-001R source manifest and canonical conformance-test count."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "manifests" / "pg-001r-source-manifest.json"
EXPECTED_KEYS = {
    "manifest_version",
    "artifact_id",
    "source_identity",
    "historical_equivalence",
    "evidence_ceiling",
    "authority",
    "expected_conformance_tests",
    "files",
}
FILE_KEYS = {"path", "sha256", "size_bytes"}


def fail(message: str) -> int:
    print(f"PG-001R manifest verification FAILED: {message}", file=sys.stderr)
    return 1


def safe_path(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise ValueError("manifest file path must be a non-empty string")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValueError(f"unsafe manifest path: {value!r}")
    return path


def count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    )


def main() -> int:
    try:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(str(exc))

    if not isinstance(payload, dict) or set(payload) != EXPECTED_KEYS:
        return fail("manifest top-level fields do not match the frozen contract")
    if payload["manifest_version"] != "1.0":
        return fail("unsupported manifest version")
    if payload["artifact_id"] != "PG-001R":
        return fail("artifact_id must be PG-001R")
    if payload["source_identity"] != "clean-room-reimplementation":
        return fail("source identity must preserve clean-room provenance")
    if payload["historical_equivalence"] is not False:
        return fail("historical equivalence must remain false")
    if payload["evidence_ceiling"] != "R2[self]":
        return fail("evidence ceiling may not exceed R2[self]")
    if payload["authority"] != "NONE":
        return fail("authority must remain NONE")
    if payload["expected_conformance_tests"] != 19:
        return fail("expected conformance test count must be exactly 19")

    files = payload["files"]
    if not isinstance(files, list) or not files:
        return fail("files must be a non-empty array")

    seen: set[PurePosixPath] = set()
    for index, entry in enumerate(files):
        if not isinstance(entry, dict) or set(entry) != FILE_KEYS:
            return fail(f"files[{index}] fields do not match the frozen contract")
        try:
            relative = safe_path(entry["path"])
        except ValueError as exc:
            return fail(str(exc))
        if relative in seen:
            return fail(f"duplicate manifest path: {relative}")
        seen.add(relative)

        digest = entry["sha256"]
        size = entry["size_bytes"]
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or digest.lower() != digest
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            return fail(f"invalid SHA-256 for {relative}")
        if type(size) is not int or size < 0:
            return fail(f"invalid size for {relative}")

        path = ROOT.joinpath(*relative.parts)
        if not path.is_file():
            return fail(f"missing file: {relative}")
        content = path.read_bytes()
        if len(content) != size:
            return fail(f"size mismatch for {relative}")
        if hashlib.sha256(content).hexdigest() != digest:
            return fail(f"SHA-256 mismatch for {relative}")

    test_path = ROOT / "packages" / "verifier" / "tests" / "test_pg001r.py"
    actual_tests = count_tests(test_path)
    if actual_tests != payload["expected_conformance_tests"]:
        return fail(f"conformance test count mismatch: expected 19, found {actual_tests}")

    print("PG-001R manifest verification PASSED")
    print(f"files verified: {len(files)}")
    print("conformance tests declared and discovered: 19")
    print("historical equivalence: false")
    print("evidence ceiling: R2[self]")
    print("authority: NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
