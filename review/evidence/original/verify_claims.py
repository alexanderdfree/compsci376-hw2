from pathlib import Path
from collections import Counter
import hashlib
import json
import os
import string
import sys
from statistics import mean

BASE=Path(__file__).resolve().parent
os.environ['NLTK_DATA']=str(BASE/'nltk_data')
sys.path.insert(0,str(BASE/'snapshot'))
import nltk
from nltk.corpus import inaugural
import improved_lm as lm

result={}
counts={}
for name in ['inaugural','gutenberg','reuters','movie_reviews','brown','abc','state_union','webtext','genesis','treebank']:
    corpus=getattr(nltk.corpus,name)
    counts[name]={'tokens':len(corpus.words()),'sentences':len(corpus.sents()),'files':len(corpus.fileids())}
result['all_corpus_sizes']=counts
tokens=list(inaugural.words())
filtered=[t for t in tokens if t not in string.punctuation]
result['independent_ngrams']={}
for label,words in [('kept',tokens),('removed',filtered)]:
    result['independent_ngrams'][label]={str(k):[(list(g),n) for g,n in Counter(zip(*(words[i:] for i in range(k)))).most_common(10)] for k in [1,2,3]}
result['removed_tokens']=len(tokens)-len(filtered)
result['distinct_flat_bigrams']=len(Counter(zip(tokens,tokens[1:])))
result['top_ten_punctuation_counts']={str(k):sum(any(lm.is_punct(t) for t in g) for g,n in Counter(zip(*(tokens[i:] for i in range(k)))).most_common(10)) for k in [2,3]}
raw=[list(s) for s in inaugural.sents()]
clean=lm.clean_sentences(raw,'keep')
result['context_alternative_punctuation_definitions']={label:{'nonalphanumeric_only':sum(any(t is not None and lm.is_punct(t) for t in key) for key in model),'nonalpha_tokens':sum(any(t is not None and not t.isalpha() for t in key) for key in model),'single_ascii_punctuation':sum(any(t is not None and t in string.punctuation for t in key) for key in model),'with_none':sum(None in key for key in model)} for label,model in [('raw',lm.build_model(raw,2)),('clean',lm.build_model(clean,2))]}
result['intervening_punctuation_to_the']=[]
for i,t in enumerate(tokens):
    if t=='to':
        j=i+1
        while j<len(tokens) and tokens[j] in string.punctuation:
            j+=1
        if j>i+1 and j<len(tokens) and tokens[j]=='the':
            result['intervening_punctuation_to_the'].append(tokens[max(0,i-4):min(len(tokens),j+5)])
result['removed_nonascii_token_examples']=Counter(t for t in tokens if any(ord(c)>127 for c in t)).most_common(20)
result['all_trigrams_in_final_examples']=[]
trained=set(g for s in clean for g in zip(s,s[1:],s[2:]))
lines=(BASE/'snapshot/output/improved_final.txt').read_text().splitlines()[1:-1]
for line in lines:
    words=line.split()
    result['all_trigrams_in_final_examples'].append({'sentence':line,'all_trigrams_seen':all(g in trained for g in zip(words,words[1:],words[2:]))})
manifest=json.loads((BASE/'source_manifest.json').read_text())
src=Path('/Users/alex/compsci376/hw2')
result['source_files_unchanged']=all((src/name).is_file() and hashlib.sha256((src/name).read_bytes()).hexdigest()==sha for name,sha in manifest.items())
(BASE/'verify_claims.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
