"""Source-level guards for the unconditional Gate Zero baseline job.

These checks prevent accidental configuration regression; they do not prove
GitHub branch protection is enforced or prevent unreviewed workflow tampering.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github' / 'workflows' / 'gate-zero-evidence.yml'

REQUIRED_COMMANDS = (
    'python tools/check_boundaries.py',
    'python tools/verify_pg001r_manifest.py',
    "-p 'test_pg001r.py'",
    "-p 'test_verify_pg001r_manifest.py'",
    "-p 'test_verify_pg001_import.py'",
)


def check_contract(source: str) -> None:
    """Refuse skipped triggering or superficial commands."""
    if not source.startswith('# New always-on aggregation check;'):
        raise ValueError('unexpected workflow contract anchor')
    if not re.search(r'(?m)^on:\s*$', source):
        raise ValueError('missing on mapping')
    block = source.split('\non:\n', 1)[1].split('\npermissions:', 1)[0]
    if not (re.search(r'(?m)^  pull_request:\s*$', block)
            and re.search(r'(?m)^  push:\s*$', block)):
        raise ValueError('missing PR or main push trigger')
    if re.search(r'(?m)^\s*(paths|paths-ignore|branches-ignore):', block):
        raise ValueError('conditional workflow trigger')
    for portion in re.split(r'(?m)^  (?:pull_request|push):\s*$', block)[1:]:
        if not re.search(r'(?m)^    branches:\s*\n      - main\s*$', portion):
            raise ValueError('event is not limited to main')
    if not re.search(r'(?m)^  gate-zero-evidence:\s*$', source):
        raise ValueError('missing unique gate-zero-evidence job')
    if re.search(r'(?m)^\s*(if:|continue-on-error:)', source):
        raise ValueError('conditional/skippable job or step')
    if '|| true' in source or re.search(r'(?m)^\s*exit 0\s*$', source):
        raise ValueError('failure-masking construct')
    if not re.search(r'(?m)^permissions:\s*\n  contents: read\s*$', source):
        raise ValueError('unexpected token permission')
    if 'persist-credentials: false' not in source:
        raise ValueError('checkout retains write credentials')
    if 'python-version: "3.12"' not in source:
        raise ValueError('unbound Python minor version')
    for cmd in REQUIRED_COMMANDS:
        if cmd not in source:
            raise ValueError(f'missing required verification: {cmd}')
    # Static acceptance is not enough: actual job must run to create valid check.


class GateZeroWorkflowTests(unittest.TestCase):
    def test_workflow_contract(self) -> None:
        check_contract(WORKFLOW.read_text(encoding='utf-8'))

    def test_refuse_each_required_command_removed(self) -> None:
        original = WORKFLOW.read_text(encoding='utf-8')
        for cmd in REQUIRED_COMMANDS:
            with self.subTest(command=cmd):
                with self.assertRaises(ValueError):
                    check_contract(original.replace(cmd, 'echo not-a-test'))

    def test_refuse_trigger_and_masking_mutations(self) -> None:
        original = WORKFLOW.read_text(encoding='utf-8')
        mutants = (
            original.replace('  pull_request:\n', ''),
            original.replace('  push:\n', ''),
            original.replace('  pull_request:\n', '  pull_request:\n    paths:\n      - "docs/**"\n'),
            original.replace('  push:\n', '  push:\n    paths-ignore:\n      - "docs/**"\n'),
            original.replace('  gate-zero-evidence:\n', '  renamed-and-not-required:\n'),
            original.replace('    runs-on: ubuntu-24.04', '    if: false\n    runs-on: ubuntu-24.04'),
            original.replace('    runs-on: ubuntu-24.04', '    continue-on-error: true\n    runs-on: ubuntu-24.04'),
            original.replace('python tools/check_boundaries.py', 'python tools/check_boundaries.py || true'),
            original.replace('  contents: read', '  contents: write'),
            original.replace('persist-credentials: false', 'persist-credentials: true'),
            original.replace('python-version: "3.12"', 'python-version: "3.x"'),
        )
        for idx, mutant in enumerate(mutants):
            with self.subTest(mutation=idx):
                with self.assertRaises(ValueError):
                    check_contract(mutant)


if __name__ == '__main__':
    unittest.main()
