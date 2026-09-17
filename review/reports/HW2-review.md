# HW2 review and verification

Your work covers all four questions in the [Canvas HW2 prompt](https://canvas.duke.edu/courses/84672/assignments/405959), and every saved output reproduces. The main corrections are in the write-up's interpretation and labeling, plus one missing setup dependency. Revise these before submitting.

Reviewed `/Users/alex/compsci376/hw2` against Canvas and the installed corpus on September 15–16, 2026. The assignment lists a September 18, 2026, 11:59 p.m. deadline. This was a review; the 28 source and output files were unchanged, verified by SHA-256.

**1. Correct the baseline label and its context counts.**

Locations: `/Users/alex/compsci376/hw2/ANSWERS.md:76`, `:112`, `:119`; `/Users/alex/compsci376/hw2/run_all.sh:33`.

The first comparison row is produced by `improved_lm.py --start uniform`, not the original generator. The rewrite strips non-ASCII characters, uses a different sampling routine, consumes fewer boundary draws, and imposes a hard cap. It is a useful controlled comparison of start strategies, but should be labeled “rewritten trigram model, uniform start.”

The actual adaptation has **68,068** contexts; **67,961** belongs to the cleaned model. Using the project's `is_punct` definition and excluding `None`, punctuation appears in **8,187/68,068 contexts (12.0%)** before cleaning and **8,041/67,961 (11.8%)** after cleaning. The claimed 8,841 is not reproduced by that definition.

An independent 500-sentence run of the actual random-start adaptation, with seed reset to 376, gives:

| Generator | Mean tokens | Verbatim copies | Capitalized starts | Terminal punctuation |
|---|---:|---:|---:|---:|
| Actual baseline adaptation | 26.844 | 0/500 | 37/500 (7.4%) | 497/500 (99.4%) |
| Rewritten generator, uniform start | 25.920 | 0/500 | 43/500 (8.6%) | 494/500 (98.8%) |

Relabeling the existing row is sufficient if the purpose is comparing configurations of the rewritten model. If you retain an “original” row, use actual baseline measurements.

**2. Fix the claims about sentence boundaries and punctuation.**

Locations: `/Users/alex/compsci376/hw2/ANSWERS.md:87`, `:92`, `:157`.

Periods are usually sentence-final, but **37 of 5,186 period tokens occur inside sentences**, including `Mr . Jefferson` and `St . Croix`. Replace “always” with “usually.” The generator ultimately stops on `None`; punctuation stripping still preserves that end-of-sentence marker. Removing written punctuation does not remove the model's ability to terminate.

Boundary starts sample observed sentence openings, including quotation marks and parentheses. There are 25 punctuation-initial training sentences. Your final 500-sentence configuration produces **four punctuation-initial outputs**, so boundary starts do not guarantee avoiding punctuation. For example:

> ( 3 ) Knowing that only a tense and unstable truce .

The explanation of the short baseline examples also needs one correction: `relationship .` starts from `('relationship', '.')`, whereas `exposition belongs .` starts from `('exposition', 'belongs')` and then generates the period.

Suggested wording: “Boundary starts greatly reduce mid-sentence fragments by sampling genuine sentence openings. Periods usually precede the end marker, but abbreviations are exceptions. Stripping punctuation removes visible clause and sentence cues while retaining `None` as the stopping symbol.”

**3. Call the length measurements tokens, or change the length calculation.**

Locations: `/Users/alex/compsci376/hw2/improved_lm.py:125`, `:142`; `/Users/alex/compsci376/hw2/ANSWERS.md:117`, `:153`.

The code uses `len(words)`, which includes commas, periods, quotes, and other punctuation tokens. The claimed “6–30 words” filter actually enforces **6–30 tokens**. In the final 500-sentence run, **41 outputs contain fewer than six nonpunctuation tokens**. For example, `The obligation on the globe .` passes with six tokens but only five nonpunctuation tokens.

The final mean is **15.882 tokens**, or **14.114 nonpunctuation tokens**. Rename the table column and prose to “tokens (including punctuation)” to keep the existing experiments valid. Only change the code and rerun the experiments if you intend a word-count constraint. Likewise, the 84 and 124 maxima are verified token counts.

**4. Do not interpret rounded percentages as exact guarantees.**

Locations: `/Users/alex/compsci376/hw2/ANSWERS.md:123`, `:125`, `:144`; `/Users/alex/compsci376/hw2/improved_lm.py:143`.

“The bigram model never copies the corpus” is false even in the saved experiment: it copies **2/500 sentences (0.4%)**, specifically `Thank you .` and `Amen .`. Integer rounding displays this as 0%.

The final model ends with terminal punctuation **498/500 times (99.6%)**, not exactly 100%. One exception is `His duty is to go to college ,`. Display one decimal place or include numerators and denominators. The final model's **0/500 exact corpus copies is correct**.

Here are the verified figures for all eight existing comparisons. Each uses 500 sentences, seed 376, and the rewritten generator's preprocessing:

| Configuration | Mean tokens | Exact copies | Capitalized starts | Terminal punctuation |
|---|---:|---:|---:|---:|
| Uniform start, trigram | 25.920 | 0 (0.0%) | 43 (8.6%) | 494 (98.8%) |
| Frequency-weighted start, trigram | 26.204 | 0 (0.0%) | 29 (5.8%) | 495 (99.0%) |
| Boundary start, trigram | 27.434 | 11 (2.2%) | 497 (99.4%) | 494 (98.8%) |
| Boundary start, trigram, strip punctuation | 26.162 | 8 (1.6%) | 498 (99.6%) | 0 (0.0%) |
| Boundary start, bigram | 28.468 | 2 (0.4%) | 499 (99.8%) | 498 (99.6%) |
| Boundary start, 4-gram | 26.130 | 89 (17.8%) | 500 (100.0%) | 495 (99.0%) |
| Boundary start, trigram, 6–30 tokens, reject copies | 15.882 | 0 (0.0%) | 496 (99.2%) | 498 (99.6%) |
| Boundary start, bigram, 6–30 tokens, reject copies | 16.270 | 0 (0.0%) | 499 (99.8%) | 497 (99.4%) |

**5. Correct the corpus's ending year.**

Locations: `/Users/alex/compsci376/hw2/ANSWERS.md:11`; `/Users/alex/compsci376/hw2/corpus_config.py:10`.

The installed corpus has 60 files and includes **`2025-Trump.txt`**, containing 3,387 tokens. Describe it as covering **1789–2025**, not ending with Biden in 2021. The reported totals—156,288 tokens and 5,395 sentences—are correct for this installed corpus.

**6. Add the sentence-tokenizer resource to setup.**

Locations: `/Users/alex/compsci376/hw2/corpus_config.py:13`; `/Users/alex/compsci376/hw2/CLAUDE.md:11`; `/Users/alex/compsci376/requirements.txt:1`.

Installing the Python package and downloading `inaugural` is insufficient on a fresh machine. With the installed corpus copied into an isolated NLTK data directory and existing tokenizer directories excluded, `basic_lm.py` fails with `Resource 'punkt_tab' not found`, followed by `ValueError: No sentence tokenizer for this corpus`.

Download `punkt_tab` during setup, or ensure it is available before `.sents()` is called:

```bash
python -m nltk.downloader inaugural punkt_tab
```

Your current machine already has the tokenizer, which is why the full rerun succeeds. NLTK's Python package and its separately downloaded resources are distinct installation steps; see [NLTK data installation](https://www.nltk.org/data.html).

**7. Make three small corrections in the frequency discussion.**

Location: `/Users/alex/compsci376/hw2/ANSWERS.md:62`.

- **Five**, not three, of the top ten bigrams contain punctuation: `, and`, `. The`, `. We`, `, the`, and `. It`. Five of the top ten trigrams is correct.
- The increase from 716 to 718 occurrences of `to the` comes from removing **double quotation marks** in two occurrences of `to " the`, rather than commas or dashes.
- `word in string.punctuation` is a **substring** test, not strictly a single-character test. For example, `!"` is a substring of `string.punctuation`. None of the removed tokens in this particular corpus is multi-character, so the reported counts are still correct. Describe the actual filter and the surviving tokens without making a universal single-character claim. See [Python membership operations](https://docs.python.org/3/reference/expressions.html#membership-test-operations).

**What passed verification**

- The write-up answers all four Canvas questions; the folder contains all five required adaptations and the generator experiments. Canvas does not specify a required numerical quality score or extra evaluation rubric on the assignment page.
- All **13 generated output files matched byte-for-byte** after running `run_all.sh` from a copied folder.
- All **60 entries** in the six-column top-ten n-gram table matched independently computed counts using adjacent-token tuples and `Counter`.
- All **ten corpus-size rows** matched the installed corpora. The large corpus comparison table is optional for the assignment, but its numbers are correct.
- The most frequent entries are correct: `the` (9,670), `of the` (1,784), `. It is` (155) with punctuation, and `the United States` (154) after filtering.
- The 68,149 distinct flat-stream bigrams and 14,329 removed tokens are correct. Flat-stream n-grams cross sentence boundaries, matching the supplied frequency scripts; `. It is` is therefore valid under that method.
- The baseline generation functions match the functions in your locally preserved instructor originals. The repaired example lookup in `basic_lm.py` is correctly explained.
- No sentence begins with lowercase `of the`; four begin with `Of the`. The leading initial bigrams are `It is` (158), `We have` (102), and `We will` (77).
- The saved 20 final sentences contain **no exact cleaned-corpus sentence copies**, and every generated trigram is present in the cleaned training sentences.
- The 4-gram sample has **8/20 copies**; its larger run has **89/500**. The Nixon example is in `1969-Nixon.txt`, and “Look, folks” is from `2021-Biden.txt`. The exact tokenized “God bless you and God bless America .” does not occur in the corpus.
- The claim that most 4-gram contexts have one continuation is supported: **113,863/124,020 contexts (91.8%)** do.

The qualitative conclusion should be more restrained. Several final outputs remain fragments or lack coherent meaning. The metrics establish better sentence openings, shorter output, and fewer verbatim copies; they do not measure grammaticality or prove that most outputs are coherent. “Some outputs are plausible short sentences, while others remain fragments or incoherent combinations” better fits the displayed examples.

Verification used Python **3.12.14**, NLTK **3.10.3**, and seed **376**. The copied `inaugural.zip` SHA-256 was `b3b2cb7bd82697b58ff79c75af20ab963810d191a8c3d1f7c240f98e5d27a895`. Results establish reproducibility in this environment; a seed alone does not pin future NLTK package or corpus versions. All eight rewritten configurations and the actual baseline were checked on 500 generated sentences each. The instructor files were inspected locally, and the current Canvas prompt and module listing were checked; remote instructor-file byte identity was not independently checked.
