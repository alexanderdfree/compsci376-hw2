import nltk
from nltk.corpus import brown
from nltk import bigrams, trigrams, FreqDist
import string

# Ensure the necessary parts of NLTK are available
nltk.download('brown')

# Tokenize the Brown corpus and filter out punctuation
tokens = [word for word in brown.words() if word not in string.punctuation]

# Create unigrams, bigrams, and trigrams
unigram_freq = FreqDist(tokens)
bigram_freq = FreqDist(bigrams(tokens))
trigram_freq = FreqDist(trigrams(tokens))

# Find the top 10 unigrams, bigrams, and trigrams
top_10_unigrams = unigram_freq.most_common(10)
top_10_bigrams = bigram_freq.most_common(10)
top_10_trigrams = trigram_freq.most_common(10)

# Print the results
print("Top 10 Unigrams:")
for word, frequency in top_10_unigrams:
    print(f"{word}: {frequency}")

print("\nTop 10 Bigrams:")
for words, frequency in top_10_bigrams:
    print(f"{words}: {frequency}")

print("\nTop 10 Trigrams:")
for words, frequency in top_10_trigrams:
    print(f"{words}: {frequency}")
