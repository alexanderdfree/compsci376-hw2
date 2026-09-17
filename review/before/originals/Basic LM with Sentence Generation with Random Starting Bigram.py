from nltk.corpus import brown
from nltk import trigrams
from collections import defaultdict
import nltk
import random

# Download necessary datasets
nltk.download('brown')
nltk.download('punkt')

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

# Function to generate sentences without needing a starting bigram
def generate_sentence():
    # Randomly choose a starting bigram
    starting_bigram = random.choice(list(model.keys()))
    text = [starting_bigram[0], starting_bigram[1]]
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
    print(generate_sentence())
