from nltk.corpus import brown
from nltk import bigrams, trigrams
from collections import Counter, defaultdict
import nltk
import random

# More comprehensive NLTK downloads
try:
    nltk.download('brown', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)  # For NLTK 3.8+
except:
    pass

# Test if brown corpus is accessible
try:
    test_sentence = brown.sents()[0]
    print("Brown corpus loaded successfully")
except Exception as e:
    print(f"Error loading brown corpus: {e}")
    print("Try running: nltk.download('all')")
    exit()

# Create a placeholder for the model
model = defaultdict(lambda: defaultdict(lambda: 0))

# Count frequency of co-occurrence
for sentence in brown.sents():
    for w1, w2, w3 in trigrams(sentence, pad_right=True, pad_left=True):
        model[(w1, w2)][w3] += 1

# Transform the counts to probabilities
for w1_w2 in model:
    total_count = float(sum(model[w1_w2].values()))
    for w3 in model[w1_w2]:
        model[w1_w2][w3] /= total_count

# Print model example
print(dict(model["part","of","the"]))

# Function to generate sentences
def generate_sentence(starting_words):
    text = starting_words
    sentence_finished = False

    while not sentence_finished:
        r = random.random()
        accumulator = 0.0

        for word in model[tuple(text[-2:])].keys():
            accumulator += model[tuple(text[-2:])][word]
            if accumulator >= r:
                text.append(word)
                break

        if text[-2:] == [None, None]:
            sentence_finished = True

    return ' '.join([t for t in text if t])

# Generate 20 sentences
for _ in range(20):
    print(generate_sentence(["part","of", "the"]))
