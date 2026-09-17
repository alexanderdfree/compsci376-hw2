# Run and verify Homework 2

[Read the assignment write-up](../README.md)

## Set up Python

From the repository root, create and activate an environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m nltk.downloader inaugural punkt_tab
```

Python 3.12.14 and NLTK 3.10.3 were used for the verified results. The dependency
file allows NLTK 3.9 or later; exact seeded results also depend on the corpus and
tokenizer data. The selected corpus has 60 inaugural addresses from 1789–2025,
156,288 tokens, and 5,395 sentences. Data downloads are not version-pinned.

The corpus loader automatically downloads the selected corpus and `punkt_tab`
when a script starts. The explicit download command above lets you complete that
setup first. NLTK normally stores resources outside the repository; set
`NLTK_DATA` if you use a custom data directory.

## Reproduce the results

With the environment active:

```bash
./run_all.sh
python src/verify.py
```

The runner uses `python3` from your active environment and seed 376. It writes all
13 generated files to [output/](../output/), including the eight 500-sentence
experiments in [comparison.txt](../output/comparison.txt). Select a different
interpreter with `PYTHON`, for example `PYTHON=python ./run_all.sh`.

The final generator configuration is:

```bash
python src/improved_lm.py --start boundary --context 2 --min-len 6 --max-len 30 --novel --seed 376
```

Lengths include punctuation tokens. Novelty means the generated sentence does not
exactly match a corpus sentence after the same preprocessing. Use
`python src/improved_lm.py --help` for the other controls.

The runner and verifier also work from another directory. After activating your
environment, substitute your clone's actual path for `/path/to/compsci376-hw2`:

```bash
/path/to/compsci376-hw2/run_all.sh
python /path/to/compsci376-hw2/src/verify.py
```

## What verification checks

- Corpus identity, sizes, context counts, and the boundary/punctuation statistics
  discussed in the write-up.
- Every entry in the 60-cell n-gram frequency table, computed independently from
  the current corpus.
- All eight comparison rows, their configuration settings, and their percentages.
- Complete quoted samples, the final sample's token limits, exact-copy rejection,
  and observed trigrams.
- The checksums of all 13 saved outputs and five unchanged instructor examples.

The verifier exits nonzero on a mismatch and writes its current result to the
ignored `.review-work/verification.json`. If the corpus differs, check the
environment and data provenance before changing the answers or expected values.
The verifier checks the current data and saved outputs; running the runner first
also checks that the code regenerates those outputs. It does not certify a new
dependency installation by reading an old success log.

## Repository guide

| Location | Contents |
|---|---|
| [README.md](../README.md) | Complete assignment write-up |
| [src/](../src/) | Frequency analyses, baseline generators, improved generator, and verifier |
| [output/](../output/) | All 13 saved experiment outputs |
| [originals/](../originals/) | Five unmodified instructor scripts |
| [verification.json](verification.json) | Tested environment, corpus provenance, expected counts, and checksums |

The initial reviews, correction evidence, and old snapshots are preserved in
[the original repository commit](https://github.com/alexanderdfree/compsci376-hw2/tree/3ad7e7ea35e79f5cdf7be70032b7762699f8db56/review).
The current branch contains the corrected assignment and the tools needed to
reproduce and check it.
