"""Adapted from originals/UnigramBigramTrigramNoPuncFreq.py: top-10 n-grams using
the original `word not in string.punctuation` filter.

Membership in a string tests substrings, not individual characters only. Many
multi-character punctuation tokens (e.g. "--", "''") survive this filter; the
script reports the remaining tokens with no alphanumeric characters.
"""
from nltk import bigrams, trigrams, FreqDist
import string

from corpus_config import corpus, CORPUS_NAME

all_tokens = corpus.words()
tokens = [word for word in all_tokens if word not in string.punctuation]

unigram_freq = FreqDist(tokens)
bigram_freq = FreqDist(bigrams(tokens))
trigram_freq = FreqDist(trigrams(tokens))

print(f"Corpus: {CORPUS_NAME}  ({len(all_tokens)} tokens, {len(tokens)} after removing punctuation)")
print("Top 10 Unigrams:")
for word, frequency in unigram_freq.most_common(10):
    print(f"{word}: {frequency}")

print("\nTop 10 Bigrams:")
for words, frequency in bigram_freq.most_common(10):
    print(f"{words}: {frequency}")

print("\nTop 10 Trigrams:")
for words, frequency in trigram_freq.most_common(10):
    print(f"{words}: {frequency}")

survivors = FreqDist(t for t in tokens if not any(ch.isalnum() for ch in t))
print("\nNon-alphanumeric tokens that survive the string.punctuation filter:")
print(survivors.most_common(15))
