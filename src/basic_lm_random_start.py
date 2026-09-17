"""Adapted from originals/Basic LM with Sentence Generation with Random Starting Bigram.py.

Same trigram model as basic_lm.py, but each sentence starts from a bigram chosen
uniformly at random from ALL distinct context bigrams in the model (including the
padding contexts (None, None) / (None, w) and bigrams that contain punctuation).

Usage: python src/basic_lm_random_start.py [seed]
"""
from nltk import trigrams
from collections import defaultdict
import random
import sys

from corpus_config import corpus, CORPUS_NAME

if len(sys.argv) > 1:
    random.seed(int(sys.argv[1]))

# Create a placeholder for the model
model = defaultdict(lambda: defaultdict(lambda: 0))

# Count frequency of co-occurrence
for sentence in corpus.sents():
    for w1, w2, w3 in trigrams(sentence, pad_right=True, pad_left=True):
        model[(w1, w2)][w3] += 1

# Transform the counts to probabilities
for w1_w2 in model:
    total_count = float(sum(model[w1_w2].values()))
    for w3 in model[w1_w2]:
        model[w1_w2][w3] /= total_count

print(f"{CORPUS_NAME}: {len(model)} distinct starting bigrams to choose from")

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
