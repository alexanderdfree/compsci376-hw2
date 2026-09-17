"""Adapted from originals/BigramFrequencies.py: most common bigram in the corpus."""
from nltk import bigrams
from collections import Counter

from corpus_config import corpus, CORPUS_NAME

tokens = corpus.words()
bigram_list = list(bigrams(tokens))
bigram_freq = Counter(bigram_list)
most_common_bigram = bigram_freq.most_common(1)

print(f"Corpus: {CORPUS_NAME}  ({len(tokens)} tokens, {len(bigram_freq)} distinct bigrams)")
print(most_common_bigram)
