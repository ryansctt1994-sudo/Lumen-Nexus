# Witness wanted — PG-001R

No independent reproduction receipt exists. Do not invent one.

If you can spare ten minutes and are not the origin implementer, run this and reply with stdout plus your OS and Python version. Do not interpret the result.

```bash
git clone https://github.com/ryansctt1994-sudo/Lumen-Nexus.git
cd Lumen-Nexus
git checkout aa52a1c854fa3d63a91c9c74a76ad2d1571197d9
python3 tools/verify_pg001r_manifest.py
python3 -m unittest discover -s packages/verifier/tests -p 'test_pg001r.py' -v
```

Expected:

- `PG-001R manifest verification PASSED`
- `Ran 19 tests` / `OK`

Fill `evidence/reproduction/PG-001R-REPRODUCTION-RECEIPT.template.json` if you want the structured form. Unsigned is fine until a signing profile exists.

A pass by the origin operator or origin hardware is `ORIGIN_RERUN` and does not close #11 or #12.
