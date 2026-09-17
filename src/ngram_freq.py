"""Adapted from originals/UnigramBigramTrigramFreq.py: top-10 uni/bi/trigrams, punctuation kept."""
from nltk import bigrams, trigrams, FreqDist

from corpus_config import corpus, CORPUS_NAME

tokens = corpus.words()

unigram_freq = FreqDist(tokens)
bigram_freq = FreqDist(bigrams(tokens))
trigram_freq = FreqDist(trigrams(tokens))

print(f"Corpus: {CORPUS_NAME}  ({len(tokens)} tokens)")
print("Top 10 Unigrams:")
for word, frequency in unigram_freq.most_common(10):
    print(f"{word}: {frequency}")

print("\nTop 10 Bigrams:")
for words, frequency in bigram_freq.most_common(10):
    print(f"{words}: {frequency}")

print("\nTop 10 Trigrams:")
for words, frequency in trigram_freq.most_common(10):
    print(f"{words}: {frequency}")
