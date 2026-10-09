#!/usr/bin/env python3
"""Fail-closed trust-domain and governance-boundary checker for Lumen Nexus."""

from __future__ import annotations

import ast
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    ROOT / "STATUS.md",
    ROOT / "AUTHORITY.md",
    ROOT / "SEAL_CONDITION.md",
    ROOT / "governance" / "CONTRADICTIONS.yaml",
    ROOT / "governance" / "EVIDENCE_LADDER.md",
    ROOT / "packages" / "contracts",
    ROOT / "packages" / "runtime",
    ROOT / "packages" / "verifier",
    ROOT / "archive",
    ROOT / "legacy" / "quarantine",
    ROOT / "research",
    ROOT / "evidence",
)

QUARANTINED_SEGMENTS = {"archive", "legacy", "research", "evidence"}
PROJECT_PREFIXES = {
    "contracts": ("lumen_contracts", "packages.contracts"),
    "runtime": ("lumen_runtime", "packages.runtime"),
    "verifier": ("lumen_verifier", "packages.verifier"),
}
FORBIDDEN_IMPORTS = {
    "contracts": PROJECT_PREFIXES["runtime"] + PROJECT_PREFIXES["verifier"],
    "runtime": PROJECT_PREFIXES["verifier"],
    "verifier": PROJECT_PREFIXES["runtime"],
}

PROHIBITION_MARKERS = (
    "production authority",
    "prohibited",
)


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    rule: str
    detail: str

    def render(self) -> str:
        relative = self.path.relative_to(ROOT) if self.path.is_relative_to(ROOT) else self.path
        return f"{relative}:{self.line}: {self.rule}: {self.detail}"


def iter_python_files(path: Path) -> Iterable[Path]:
    if not path.exists():
        return ()
    return (
        candidate
        for candidate in path.rglob("*.py")
        if "__pycache__" not in candidate.parts
    )


def import_targets(tree: ast.AST) -> Iterable[tuple[str, int, int]]:
    """Yield qualified import names, retaining relative levels for resolution.

    Include from-import names: checking only ``node.module`` misses
    ``from packages import runtime`` and its aliased equivalent.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, node.lineno, 0
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                target = f"{module}.{alias.name}" if module else alias.name
                yield target, node.lineno, node.level


def starts_with_any(module: str, prefixes: tuple[str, ...]) -> bool:
    return any(module == prefix or module.startswith(prefix + ".") for prefix in prefixes)


def check_required_paths() -> list[Violation]:
    violations: list[Violation] = []
    for path in REQUIRED_PATHS:
        if not path.exists():
            violations.append(Violation(path, 1, "required-path", "missing"))
    return violations


def check_root_prohibitions() -> list[Violation]:
    violations: list[Violation] = []
    for path in (ROOT / "STATUS.md", ROOT / "AUTHORITY.md", ROOT / "SEAL_CONDITION.md"):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for marker in PROHIBITION_MARKERS:
            if marker not in text:
                violations.append(
                    Violation(path, 1, "authority-marker", f"missing required marker {marker!r}")
                )
    return violations


def check_domain(domain: str) -> list[Violation]:
    base = ROOT / "packages" / domain
    violations: list[Violation] = []

    for path in iter_python_files(base):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            line = getattr(exc, "lineno", 1) or 1
            violations.append(Violation(path, line, "parse", str(exc)))
            continue

        for module, line, relative_level in import_targets(tree):
            if relative_level:
                package = path.parent.relative_to(ROOT).parts
                keep = len(package) - relative_level + 1
                module = ".".join((*package[:max(keep, 0)], module))
                if keep <= 0 or not starts_with_any(module, (f"packages.{domain}",)):
                    violations.append(
                        Violation(
                            path,
                            line,
                            "relative-import",
                            "imports may not escape the trust-domain package root",
                        )
                    )

            if module == "packages.*":
                violations.append(Violation(
                    path, line, "ambiguous-import",
                    "project-root wildcard imports cannot establish a trust domain",
                ))

            if starts_with_any(module, FORBIDDEN_IMPORTS[domain]):
                violations.append(
                    Violation(
                        path,
                        line,
                        "trust-domain-import",
                        f"{domain} may not import {module!r}",
                    )
                )

            first_segment = module.split(".", 1)[0] if module else ""
            if first_segment in QUARANTINED_SEGMENTS:
                violations.append(
                    Violation(
                        path,
                        line,
                        "quarantine-import",
                        f"runtime domains may not import from {first_segment!r}",
                    )
                )

    return violations


def check_no_python_in_quarantine() -> list[Violation]:
    violations: list[Violation] = []
    for root in (
        ROOT / "archive",
        ROOT / "legacy" / "quarantine",
        ROOT / "research",
        ROOT / "evidence",
    ):
        for path in iter_python_files(root):
            violations.append(
                Violation(
                    path,
                    1,
                    "quarantine-executable",
                    "Python source is prohibited in non-runtime evidence/quarantine domains",
                )
            )
    return violations


def main() -> int:
    violations: list[Violation] = []
    violations.extend(check_required_paths())
    violations.extend(check_root_prohibitions())
    for domain in ("contracts", "runtime", "verifier"):
        violations.extend(check_domain(domain))
    violations.extend(check_no_python_in_quarantine())

    if violations:
        print("Trust-boundary check FAILED", file=sys.stderr)
        ordered = sorted(violations, key=lambda item: (str(item.path), item.line, item.rule))
        for violation in ordered:
            print(f"- {violation.render()}", file=sys.stderr)
        return 1

    print("Trust-boundary check PASSED")
    print("contracts: zero project-domain dependencies")
    print("runtime: contracts-only project dependency")
    print("verifier: read-only domain, contracts-only project dependency")
    print("archive/legacy/research/evidence: no executable Python")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
