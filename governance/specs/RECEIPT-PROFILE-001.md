# RECEIPT-PROFILE-001: Origin Ledger and Witness Envelope Boundary

- **Status:** DRAFT CANDIDATE
- **Date:** 2026-07-21
- **Authority:** NONE
- **Related ADR:** ADR-0006
- **Related contradiction:** C-RCPT-001

## Purpose

This profile separates an origin-generated hash-linked ledger receipt from independently verifiable witness evidence. It prevents a caller-controlled string from being treated as witness identity binding and prevents origin execution from silently promoting itself above its evidence ceiling.

## Origin receipt

An origin receipt contains:

- `seq`: zero-based ledger sequence assigned only by the ledger;
- `predecessor_digest`: the prior committed receipt digest or the fixed genesis sentinel;
- `event_canonical_bytes`: the exact immutable bytes admitted by the ledger;
- `event_canonical_sha256`: SHA-256 over `event_canonical_bytes`;
- `canon_profile`: the canonicalization profile identifier;
- `witness_identity_binding`: `null` for every origin receipt;
- `receipt_digest`: SHA-256 over the canonical receipt core.

An origin receipt proves only that the candidate ledger produced a particular internally linked record under the declared profile. It does not prove independent execution, witness identity, historical equivalence, or repair closure.

## Witness envelope

A witness envelope is a separate artifact. It must not be created through `ReceiptLedger.append()` and must not mutate the origin receipt.

A future accepted witness envelope must bind at minimum:

- the complete origin `receipt_digest`;
- the witness public-key or authenticated-principal identifier;
- the identity-binding method and profile version;
- the witness signature or equivalent authenticated attestation;
- the source-tree digest;
- the environment digest;
- the executed test-manifest digest;
- the execution result digest;
- an anti-replay value such as a challenge, nonce, or trusted timestamp;
- the witness screening or independence disposition.

## Eligibility rule

A non-null identity label alone is never sufficient. Evidence at or above the repository's R3 boundary requires both:

1. a non-null receipt digest bound to the executed artifact set; and
2. a witness identity binding that is cryptographically or operationally verified under an accepted witness profile.

Until that profile, verifier, screening procedure, and key-management process are accepted, all receipts emitted by the candidate ledger remain origin/self receipts and are ineligible for witness promotion.

## Verification behavior

The ADR-0006 ledger verifier:

- verifies retained event bytes against their event digest;
- verifies sequence, predecessor linkage, canonicalization profile, and receipt digest;
- rejects non-null witness metadata on an origin receipt;
- performs no repair, mutation, key lookup, network access, or authority decision.

Witness-envelope verification belongs to a separate read-only verifier and must fail closed when identity material, signatures, source bindings, environment bindings, or replay protection are absent or invalid.

## Concurrency semantics

The ledger guarantees linearizability: concurrent successful appends are committed in one gapless, unambiguous order under the ledger lock. It does not claim that operating-system thread scheduling will reproduce the same order in a separate run.

## Non-claims

This profile does not:

- close `C-RCPT-001`;
- establish historical equivalence with missing PG-001 artifacts;
- create an independent witness;
- raise the ecosystem evidence ceiling;
- grant pilot or production authority;
- define final signature algorithms, trust anchors, key rotation, revocation, persistence, or recovery.

## Acceptance dependencies

Before this profile can advance, the steward must approve:

- the signature and identity-binding profile;
- witness screening and independence criteria;
- source, environment, and manifest digest formats;
- nonce or timestamp replay protection;
- key rotation and revocation behavior;
- persistence and recovery semantics;
- a clean-clone repair-receipt procedure;
- an explicit gate decision.
