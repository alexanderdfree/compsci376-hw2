"""Single place to choose which NLTK corpus every script in this repo uses.

The instructor's originals (in originals/) hard-code the Brown corpus.  Every
adapted script imports `corpus` from here instead, so switching corpora is a
one-line change.  A corpus must expose .words() and .sents() (all of the
plaintext corpora do: brown, gutenberg, inaugural, state_union, webtext, ...).
"""
import nltk

CORPUS_NAME = "inaugural"  # Installed corpus: inaugural addresses, 1789-2025


def load_corpus(name=CORPUS_NAME):
    # Plaintext corpus readers need sentence-tokenizer data as well as the corpus.
    # Installing the nltk Python package alone does not install these resources.
    nltk.download(name, quiet=True, raise_on_error=True)
    nltk.download("punkt_tab", quiet=True, raise_on_error=True)
    return getattr(nltk.corpus, name)


corpus = load_corpus()
