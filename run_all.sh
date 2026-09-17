#!/usr/bin/env bash
# Regenerates output/ with a fixed seed; exact results also depend on NLTK and corpus data.
# Usage: ./run_all.sh                  (uses python3 from the active environment)
#        PYTHON=python ./run_all.sh    (override the interpreter)
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
SEED=376
mkdir -p output

"$PYTHON" src/bigram_frequencies.py            > output/bigram_frequencies.txt
"$PYTHON" src/ngram_freq.py                    > output/ngram_freq.txt
"$PYTHON" src/ngram_freq_nopunct.py            > output/ngram_freq_nopunct.txt
"$PYTHON" src/basic_lm.py "$SEED"              > output/basic_lm.txt
"$PYTHON" src/basic_lm_random_start.py "$SEED" > output/basic_lm_random_start.txt

# Tweaked generator: one file per experiment (20 sentences each).
"$PYTHON" src/improved_lm.py --start uniform  --seed "$SEED" > output/improved_uniform_start.txt
"$PYTHON" src/improved_lm.py --start frequent --seed "$SEED" > output/improved_frequent_start.txt
"$PYTHON" src/improved_lm.py --start boundary --seed "$SEED" > output/improved_boundary_start.txt
"$PYTHON" src/improved_lm.py --start boundary --punct strip --seed "$SEED" > output/improved_boundary_nopunct.txt
"$PYTHON" src/improved_lm.py --start boundary --context 1 --seed "$SEED" > output/improved_bigram_model.txt
"$PYTHON" src/improved_lm.py --start boundary --context 3 --seed "$SEED" > output/improved_4gram_model.txt
"$PYTHON" src/improved_lm.py --start boundary --min-len 6 --max-len 30 --novel --seed "$SEED" > output/improved_final.txt

# Summary statistics over 500 sentences per rewritten-generator configuration.
# The uniform-start row uses the cleaned model, not the untouched baseline.
{
  for cfg in "--start uniform" "--start frequent" "--start boundary" \
             "--start boundary --punct strip" "--start boundary --context 1" \
             "--start boundary --context 3" "--start boundary --min-len 6 --max-len 30 --novel" \
             "--start boundary --context 1 --min-len 6 --max-len 30 --novel"; do
    # shellcheck disable=SC2086
    "$PYTHON" src/improved_lm.py $cfg -n 500 --quiet --seed "$SEED"
    echo
  done
} > output/comparison.txt
echo "done: $(ls output | wc -l | tr -d ' ') files in output/"
