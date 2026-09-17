import nltk
from nltk.corpus import brown
from nltk import bigrams
from collections import Counter

# Ensure the necessary parts of NLTK are available
nltk.download('brown')

# Tokenize the Brown corpus
tokens = brown.words()

# Create bigrams from the tokens
bigram_list = list(bigrams(tokens))

# Count the frequency of each bigram
bigram_freq = Counter(bigram_list)

# Find the most common bigram
most_common_bigram = bigram_freq.most_common(1)

print(most_common_bigram)
