# HW2 corrections implemented

Updated the working files in `/Users/alex/compsci376/hw2` and regenerated all 13 files in its `output/` directory.

- Corrected corpus coverage to 1789–2025 and the raw/cleaned context counts.
- Labeled the comparison as configurations of the rewritten generator.
- Corrected period, boundary-start, punctuation-filter, and frequency explanations.
- Labeled lengths as tokens including punctuation throughout the write-up, CLI help, and generated statistics.
- Reported percentages to one decimal place, with exact copy counts, and removed unsupported guarantees about copying or coherence.
- Added automatic `punkt_tab` installation and documented explicit setup.
- Updated the project guidance to match the implemented behavior.

Verification passed: all 60 n-gram table entries, all eight 500-sentence comparison configurations, and all quoted complete sentence examples match the data or generated outputs. An isolated installation without tokenizer data successfully downloaded `punkt_tab` and ran the baseline generator. The five baseline output files are unchanged; the eight rewritten-generator output files differ only in their summary text. Instructor originals and model generation logic remain unchanged.

`HW2-ANSWERS.md` is a copy of the corrected working write-up. The earlier `HW2-review.md` records the findings before these corrections; `HW2-corrections-verification.json` records the completed verification.
