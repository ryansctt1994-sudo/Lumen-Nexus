# C-RCPT-001 quarantine map

**Status:** Historical dual-owner modules were never imported into this repository.  
**Contradiction:** OPEN  
**Candidate replacement:** draft PR #29 (`packages/runtime/lumen_runtime/receipt_ledger.py`)  
**Authority:** NONE

## Historical path

| Module | Location |
|---|---|
| `hashchain.py` | Not present. Slot reserved at `legacy/quarantine/hashchain/` |
| `receipt.py` | Not present. Do not reconstruct from memory and treat as original. |

If either file is later found, import it here with original bytes and digest. Do not execute it from the runtime package path.

## Active candidate

| Module | Location | Status |
|---|---|---|
| `ReceiptLedger` | PR #29 `packages/runtime/lumen_runtime/receipt_ledger.py` | Candidate, not accepted |
| Tests | PR #29 `packages/runtime/tests/test_receipt_ledger.py` | Candidate |
| ADR | `governance/adr/ADR-0006-receipt-ledger.md` | Candidate implementation — not accepted |

## Closure still requires

1. Steward acceptance of ADR-0006.
2. Clean-clone repair receipt.
3. Explicit gate decision.
4. This map remaining accurate after merge.

PR #29 existing does not close C-RCPT-001.
