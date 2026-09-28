#!/usr/bin/env bash
# PG-001R clean-clone helper. Does not issue an independent receipt.
set -euo pipefail

PINNED_COMMIT="aa52a1c854fa3d63a91c9c74a76ad2d1571197d9"
REPO_URL="https://github.com/ryansctt1994-sudo/Lumen-Nexus.git"
WORKDIR="${1:-pg001r-repro}"

if [[ -e "${WORKDIR}" ]]; then
  echo "refusing to reuse existing path: ${WORKDIR}" >&2
  exit 2
fi

git clone "${REPO_URL}" "${WORKDIR}"
cd "${WORKDIR}"
git checkout "${PINNED_COMMIT}"
ACTUAL="$(git rev-parse HEAD)"
if [[ "${ACTUAL}" != "${PINNED_COMMIT}" ]]; then
  echo "commit mismatch: expected ${PINNED_COMMIT}, got ${ACTUAL}" >&2
  exit 2
fi

echo "python: $(python3 --version 2>&1)"
echo "uname: $(uname -a)"
echo "commit: ${ACTUAL}"

python3 tools/verify_pg001r_manifest.py
python3 -m unittest discover -s packages/verifier/tests -p 'test_pg001r.py' -v

echo "PG-001R clean-clone commands completed."
echo "This script does not classify independence and does not close #11 or #12."
