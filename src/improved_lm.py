"""Tweaked version of originals/Basic LM with Sentence Generation with Random Starting Bigram.py.

The original builds a trigram model (context = previous 2 words) and starts each
sentence from a bigram chosen uniformly from every distinct context in the model,
so most outputs begin mid-phrase ("of magnanimity , one home , take it .").
This script keeps the same counting/sampling idea but makes the knobs explicit:

  --context K      tokens of context (1 = bigram LM, 2 = trigram LM as in the
                   original, 3 = 4-gram LM)
  --start HOW      boundary  start from the None padding, so the first words are
                             drawn from the sentence-initial distribution (default)
                   uniform   any context, equally likely, in the cleaned model
                   frequent  a non-padding context chosen in proportion to its
                             corpus frequency (demonstrates why "frequent" is not
                             the same as "good starting point")
  --punct MODE     keep (default) or strip punctuation tokens before training
  --min-len/--max-len   reject sentences outside this token range, including punctuation
  --novel          reject exact matches to cleaned corpus sentences
  --quiet          print only the summary statistics

Non-ASCII characters are always stripped from tokens: the post-2009 inaugural files
are decoded as Latin-1 by NLTK, which turns curly quotes and em-dashes into
junk tokens such as '\\x80\\x94' and glues an 'â' onto the preceding word.
Uniform starts use the original start-selection strategy, but preprocessing,
sampling, stopping, and the hard cap differ from the baseline implementation.

Examples:
  python src/improved_lm.py --seed 376
  python src/improved_lm.py --start uniform --seed 376        # compare start strategies
  python src/improved_lm.py --context 1 --punct strip -n 10
  python src/improved_lm.py --min-len 6 --max-len 30 --novel -n 500 --quiet
"""
import argparse
import random
import re
from collections import Counter, defaultdict

from nltk.util import ngrams

from corpus_config import CORPUS_NAME, load_corpus

NON_ASCII = re.compile(r"[^\x00-\x7f]")
TERMINAL = {".", "!", "?", '."', '?"', '!"', "...", "...."}
HARD_CAP = 200  # tokens; stops a sentence that never reaches the end padding


def is_punct(token):
    return not any(ch.isalnum() for ch in token)


def clean_sentences(sents, punct):
    cleaned = []
    for sent in sents:
        tokens = []
        for token in sent:
            token = NON_ASCII.sub("", token)
            if not token or (punct == "strip" and is_punct(token)):
                continue
            tokens.append(token)
        if tokens:
            cleaned.append(tokens)
    return cleaned


def build_model(sents, k):
    """model[context tuple of k tokens] -> Counter of next token (None = boundary)."""
    model = defaultdict(Counter)
    for sent in sents:
        for gram in ngrams(sent, k + 1, pad_left=True, pad_right=True):
            model[gram[:-1]][gram[-1]] += 1
    return model


def choose_start(model, k, how, rng):
    if how == "boundary":
        return (None,) * k
    if how == "uniform":
        return rng.choice(list(model.keys()))
    if how == "frequent":
        keys = [key for key in model if None not in key]
        weights = [sum(model[key].values()) for key in keys]
        return rng.choices(keys, weights=weights)[0]
    raise ValueError(how)


def generate(model, k, start, rng):
    text = list(start)
    while len(text) < HARD_CAP:
        counter = model.get(tuple(text[-k:]))
        if not counter:
            break
        word = rng.choices(list(counter.keys()), weights=list(counter.values()))[0]
        if word is None:
            break
        text.append(word)
    return [t for t in text if t is not None]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default=CORPUS_NAME)
    ap.add_argument("--context", type=int, default=2, help="tokens of context (default 2 = trigram LM)")
    ap.add_argument("--start", choices=["boundary", "uniform", "frequent"], default="boundary")
    ap.add_argument("--punct", choices=["keep", "strip"], default="keep")
    ap.add_argument("--min-len", type=int, default=1, help="minimum tokens, including punctuation")
    ap.add_argument("--max-len", type=int, default=0, help="maximum tokens, including punctuation; 0 = no upper-length filter")
    ap.add_argument("--novel", action="store_true", help="reject exact matches to cleaned corpus sentences")
    ap.add_argument("-n", type=int, default=20, help="sentences to generate")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    corpus = load_corpus(args.corpus)
    sents = clean_sentences(corpus.sents(), args.punct)
    seen = {" ".join(s) for s in sents}
    model = build_model(sents, args.context)

    print(f"corpus={args.corpus} sentences={len(sents)} context={args.context} "
          f"start={args.start} punct={args.punct} min_len={args.min_len} "
          f"max_len={args.max_len or 'inf'} novel={args.novel} seed={args.seed} "
          f"contexts={len(model)}")

    outputs, attempts, rejected = [], 0, Counter()
    while len(outputs) < args.n and attempts < 200 * args.n:
        attempts += 1
        words = generate(model, args.context, choose_start(model, args.context, args.start, rng), rng)
        if len(words) < args.min_len or (args.max_len and len(words) > args.max_len):
            rejected["length"] += 1
            continue
        if args.novel and " ".join(words) in seen:
            rejected["verbatim"] += 1
            continue
        outputs.append(words)

    if not args.quiet:
        for words in outputs:
            print(" ".join(words))

    n = len(outputs) or 1
    verbatim = sum(" ".join(w) in seen for w in outputs)
    capitalized = sum(w[0][:1].isupper() for w in outputs)
    terminal = sum(w[-1] in TERMINAL for w in outputs)
    mean_len = sum(len(w) for w in outputs) / n
    print(f"--- {len(outputs)} sentences, mean length {mean_len:.1f} tokens, "
          f"verbatim copies of cleaned corpus sentences {verbatim}/{n} ({100*verbatim/n:.1f}%), "
          f"start with a capital {capitalized}/{n} ({100*capitalized/n:.1f}%), "
          f"end with terminal punctuation {terminal}/{n} ({100*terminal/n:.1f}%), "
          f"rejected {dict(rejected) or 0}")


if __name__ == "__main__":
    main()
