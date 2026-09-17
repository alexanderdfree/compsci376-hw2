# COMPSCI 376 — Homework 2

N-gram frequency analysis and sentence generation using NLTK's inaugural-address
corpus for Duke's Computational Approaches to Human Language course.

The corrected write-up is [ANSWERS.md](ANSWERS.md). It covers corpus selection,
unigram/bigram/trigram frequencies, punctuation effects, and experiments to improve
sentence generation.

## Run the experiments

Use Python 3.12 or a compatible version, then install the dependencies and NLTK data:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m nltk.downloader inaugural punkt_tab
PYTHON=python ./run_all.sh
```

The corpus loader also downloads the selected corpus and `punkt_tab` automatically.
The script regenerates all 13 files in `output/`, using seed 376. The checked
environment was Python 3.12.14 with NLTK 3.10.3 and 60 inaugural addresses spanning
1789–2025. Exact output depends on the corpus and tokenizer versions as well as the
seed; NLTK data downloads are not version-pinned.

To run the final generator configuration:

```bash
python improved_lm.py --start boundary --context 2 --min-len 6 --max-len 30 --novel --seed 376
```

Lengths count tokens, including punctuation. The novelty filter rejects exact
matches to corpus sentences after the same preprocessing as the model.

## Files

| Path | Contents |
|---|---|
| `ANSWERS.md` | Corrected assignment write-up |
| `corpus_config.py` | Corpus selection and NLTK resource setup |
| `bigram_frequencies.py`, `ngram_freq.py`, `ngram_freq_nopunct.py` | Frequency analyses |
| `basic_lm.py`, `basic_lm_random_start.py` | Adaptations of the instructor's generators |
| `improved_lm.py` | Generator with configurable starts, order, punctuation, and filtering |
| `run_all.sh`, `output/` | Reproduction command and saved experiment results |
| `originals/` | Unmodified instructor examples |
| `review/` | Review reports, evidence, historical snapshot, and verification script |

## Verify the work

After regenerating the outputs, run:

```bash
python review/verify.py
```

This checks all 60 entries in the n-gram frequency table, all eight 500-sentence
comparison configurations, the displayed sentence examples, and preservation of
the instructor examples and model generation logic. Results and a correction diff
are written to `.review-work/`, which Git ignores.

The review includes a successful isolated-install test in which `punkt_tab` was
initially absent. The verification script checks that saved evidence; it does not
repeat the installation test. See [review/README.md](review/README.md) for the
historical reports and evidence.
