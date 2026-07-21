# Frozen Baselines

This directory is reserved for immutable baseline artifacts and manifests used in reproduction.

## Admission requirements

A baseline must include:

- a complete, non-abbreviated cryptographic digest;
- artifact size and media type;
- source and build provenance;
- dependency and toolchain anchors;
- governance-bundle identifier;
- reproduction instructions;
- evidence level and authority ceiling;
- known contradictions and limitations.

## Current state

The documented WeaverX master bundle and P1-Baseline-RC1 image have **not** been imported. Abbreviated hashes in the handoff are references, not usable build anchors. `C-ANCHOR-001` remains OPEN.