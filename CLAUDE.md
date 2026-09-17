# HW2 working guidance

- `README.md` is the canonical assignment write-up. Keep its four answers, tables,
  and sample quotations consistent with the saved results.
- `src/` contains the seven adapted scripts and `verify.py`. Corpus selection and
  resource setup are in `src/corpus_config.py`.
- Preserve all five instructor scripts in `originals/` byte-for-byte.
- Run `./run_all.sh` with the project environment active, or select an interpreter
  with `PYTHON`. Run `python src/verify.py` to check the current assignment.
- Keep seed 376 and generation behavior unchanged during organizational edits.
  Regenerate all 13 outputs and compare them after structural changes.
- Lengths count tokens including punctuation. Comparison rows describe the
  rewritten generator, and copy checks use identically cleaned corpus sentences.
- `docs/SETUP.md` contains the setup commands and repository guide.
  `docs/verification.json` records provenance and expected checksums. Investigate
  mismatches before changing this manifest; update it only for intended, verified
  changes to the assignment or data.
- Verification artifacts belong in the ignored `.review-work/` directory.
  Historical reviews and snapshots remain in Git history.
