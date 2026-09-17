from pathlib import Path
from collections import Counter
import contextlib
import hashlib
import io
import json
import os
import random
import runpy
import string
import sys

BASE = Path(__file__).resolve().parent
PROJECT = BASE / 'snapshot'
os.environ['NLTK_DATA'] = str(BASE / 'nltk_data')
sys.path.insert(0, str(PROJECT))
import nltk
import improved_lm as lm
from nltk.corpus import inaugural

def record(name, value):
    result[name] = value

def summary(outputs, sents):
    seen = {tuple(s) for s in sents}
    n = len(outputs)
    return {'n': n, 'mean_tokens': sum(map(len, outputs))/n,
            'mean_lexical_tokens': sum(sum(not lm.is_punct(w) for w in s) for s in outputs)/n,
            'copies': sum(tuple(s) in seen for s in outputs),
            'capitalized': sum(s[0][0].isupper() for s in outputs),
            'terminal': sum(s[-1] in lm.TERMINAL for s in outputs),
            'punctuation_starts': sum(lm.is_punct(s[0]) for s in outputs)}

result = {}
raw = [list(s) for s in inaugural.sents()]
clean = lm.clean_sentences(raw, 'keep')
raw_model = lm.build_model(raw, 2)
clean_model = lm.build_model(clean, 2)
record('environment', {'python':sys.version, 'nltk':nltk.__version__, 'corpus_root':str(inaugural.root), 'encoding':inaugural.encoding('2021-Biden.txt')})
record('fileids', inaugural.fileids())
record('corpus', {'words':len(inaugural.words()),'sentences':len(raw),'files':len(inaugural.fileids()),'last_file_tokens':len(inaugural.words('2025-Trump.txt'))})
record('rerun', {'matching':[p.name for p in (PROJECT/'output').glob('*.txt') if p.read_bytes()==(BASE/'rerun/output'/p.name).read_bytes()],
                 'different':[p.name for p in (PROJECT/'output').glob('*.txt') if p.read_bytes()!=(BASE/'rerun/output'/p.name).read_bytes()],
                 'log':(BASE/'run_all.log').read_text()[-2000:]})
record('contexts', {name:{'total':len(model),'containing_punctuation':sum(any(t is not None and lm.is_punct(t) for t in key) for key in model)} for name,model in [('raw',raw_model),('cleaned',clean_model)]})
record('initial_bigrams', [(list(k),n) for k,n in Counter(tuple(s[:2]) for s in raw).most_common(10)])
record('of_the_starts', {'lower':sum(s[:2]==['of','the'] for s in raw),'upper':sum(s[:2]==['Of','the'] for s in raw)})
periods = Counter()
period_examples = []
punct_start_examples = []
for fid in inaugural.fileids():
    for sent in inaugural.sents(fid):
        if sent and lm.is_punct(sent[0]):
            punct_start_examples.append({'file':fid,'sentence':' '.join(sent)})
        for i,w in enumerate(sent):
            if w == '.':
                after = sent[i+1] if i+1<len(sent) else '<EOS>'
                periods[after] += 1
                if after != '<EOS>' and len(period_examples)<6:
                    period_examples.append({'file':fid,'sentence':' '.join(sent),'after':after})
record('after_period',periods.most_common())
record('period_nonterminal_examples',period_examples)
record('punctuation_sentence_starts',{'n':len(punct_start_examples),'examples':punct_start_examples[:8]})

buffer=io.StringIO()
with contextlib.redirect_stdout(buffer):
    old_argv=sys.argv
    sys.argv=['basic_lm_random_start.py','376']
    baseline=runpy.run_path(str(PROJECT/'basic_lm_random_start.py'))
    sys.argv=old_argv
baseline['random'].seed(376)
baseline_outputs=[baseline['generate_sentence']().split() for _ in range(500)]
record('actual_baseline_500',summary(baseline_outputs,raw))

class Tracker(random.Random):
    def __init__(self,seed):
        super().__init__(seed)
        self.starts=[]
    def choice(self,seq):
        value=super().choice(seq)
        self.starts.append(value)
        return value

tracker=Tracker(376)
baseline['generate_sentence'].__globals__['random']=tracker
twenty=[baseline['generate_sentence']() for _ in range(20)]
record('short_baseline_starts',[{'output':o,'start':list(s)} for o,s in zip(twenty,tracker.starts) if len(o.split())<=4])

configs=[('uniform',2,'keep',1,0,False),('frequent',2,'keep',1,0,False),('boundary',2,'keep',1,0,False),('boundary',2,'strip',1,0,False),('boundary',1,'keep',1,0,False),('boundary',3,'keep',1,0,False),('boundary',2,'keep',6,30,True),('boundary',1,'keep',6,30,True)]
rows=[]
for start,k,punct,lo,hi,novel in configs:
    sents=lm.clean_sentences(raw,punct)
    seen={tuple(s) for s in sents}
    model=lm.build_model(sents,k)
    rng=random.Random(376)
    outputs=[]
    rejections=Counter()
    while len(outputs)<500:
        words=lm.generate(model,k,lm.choose_start(model,k,start,rng),rng)
        if len(words)<lo or (hi and len(words)>hi):
            rejections['length']+=1
        elif novel and tuple(words) in seen:
            rejections['verbatim']+=1
        else:
            outputs.append(words)
    row={'config':[start,k,punct,lo,hi,novel],**summary(outputs,sents),'rejections':dict(rejections),'contexts':len(model), 'single_successor_contexts':sum(len(c)==1 for c in model.values())}
    if k==1 and not novel:
        row['copy_examples']=[' '.join(s) for s in outputs if tuple(s) in seen]
    if novel and k==2:
        row['under_6_lexical_tokens']=[' '.join(s) for s in outputs if sum(not lm.is_punct(w) for w in s)<6]
        row['nonterminal_examples']=[' '.join(s) for s in outputs if s[-1] not in lm.TERMINAL]
        row['punctuation_start_examples']=[' '.join(s) for s in outputs if lm.is_punct(s[0])]
        (BASE/'final_500.txt').write_text('\n'.join(' '.join(s) for s in outputs)+'\n')
    rows.append(row)
record('configurations',rows)
record('sample_lengths', {name:max(map(lambda s:len(s.split()),(PROJECT/'output'/name).read_text().splitlines()[2 if name=='basic_lm.txt' else 1:-1 if name.startswith('improved') else None])) for name in ['basic_lm.txt','improved_boundary_nopunct.txt']})
record('multi_character_punctuation_removed',Counter(t for t in inaugural.words() if t in string.punctuation and len(t)>1).most_common())

seen={tuple(s) for s in clean}
for name in ['improved_final.txt','improved_4gram_model.txt']:
    lines=(PROJECT/'output'/name).read_text().splitlines()[1:-1]
    record(name,{'sentences':len(lines),'copies':sum(tuple(line.split()) in seen for line in lines)})
record('quotation_sources', {quote:[fid for fid in inaugural.fileids() if quote in ' '.join(inaugural.words(fid))] for quote in ['We see tasks that need doing , waiting for hands to do them .','God bless you and God bless America .','Look , folks']})
(BASE/'audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
