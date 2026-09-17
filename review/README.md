# HW2 review record

The repository root contains the corrected assignment. This directory preserves
the review, implementation evidence, and code used to verify it.

| Path | Purpose |
|---|---|
| `reports/HW2-review.md` | Original findings before corrections |
| `reports/HW2-verification.json` | Original numerical verification |
| `reports/HW2-corrections.md` | Summary of implemented corrections |
| `reports/HW2-corrections-verification.json` | Completed correction checks |
| `before/` | Assignment files and outputs before the corrections |
| `evidence/original/` | Detailed initial audit, corpus checks, 500 generated sentences, scripts, and logs |
| `evidence/corrections/` | Correction diff, verification results, scripts, and isolated-install evidence |
| `verify.py` | Verification entry point that works from any clone location |

Run `python review/verify.py` with the project dependencies installed. Its new
results go to the ignored `.review-work/` directory; it leaves historical evidence
unchanged. Assertions are tied to the corpus used for this assignment, so a future
corpus release can require refreshing both outputs and the write-up.

Files under `evidence/`, `reports/`, and `before/` are historical records from the
September 15–16 review. They intentionally preserve original statements, local
paths, and script contents, including findings later corrected. Archived scripts
can reference the original machine's working directories; use `verify.py` for the
supported portable checks. In particular, the original failed tokenizer setup
test is followed by a successful test in `evidence/corrections/fresh_setup.json`.

NLTK corpus downloads, tokenizer caches, virtual environments, and duplicate
temporary rerun directories are not included. Setup instructions are in the main
README, and the original corpus archive hash is recorded in the verification data.
