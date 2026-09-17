from collections import Counter
from pathlib import Path
import ast
import difflib
import hashlib
import json
import re
import sys

BASE = Path(__file__).resolve().parent
SRC = Path('/Users/alex/compsci376/hw2')
BEFORE = BASE / 'before'
sys.path.insert(0, str(SRC))
from corpus_config import corpus
import improved_lm as lm

checks = {}
def check(name, condition):
    checks[name] = bool(condition)
    assert condition, name

unchanged, summary_only = [], []
for before in sorted((BEFORE / 'output').glob('*.txt')):
    after = SRC / 'output' / before.name
    old, new = before.read_text().splitlines(), after.read_text().splitlines()
    if old == new:
        unchanged.append(before.name)
    else:
        check('only_summary_changed_' + before.name,
              [s for s in old if not s.startswith('--- ')] ==
              [s for s in new if not s.startswith('--- ')])
        summary_only.append(before.name)
check('all_13_outputs_regenerated', len(unchanged) + len(summary_only) == 13)
check('five_baseline_outputs_unchanged', len(unchanged) == 5)

check('instructor_originals_unchanged', all(
    p.read_bytes() == (SRC / 'originals' / p.name).read_bytes()
    for p in (BEFORE / 'originals').glob('*.py')))
old_tree = ast.parse((BEFORE / 'improved_lm.py').read_text())
new_tree = ast.parse((SRC / 'improved_lm.py').read_text())
for name in ['is_punct', 'clean_sentences', 'build_model', 'choose_start', 'generate']:
    pick = lambda tree: ast.dump(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name))
    check('model_function_unchanged_' + name, pick(old_tree) == pick(new_tree))

tokens = list(corpus.words())
raw = [list(s) for s in corpus.sents()]
clean = lm.clean_sentences(raw, 'keep')
raw_model, clean_model = lm.build_model(raw, 2), lm.build_model(clean, 2)
check('corpus_dates_and_sizes', corpus.fileids()[-1] == '2025-Trump.txt' and
      (len(corpus.fileids()), len(tokens), len(raw)) == (60, 156288, 5395))
check('raw_and_clean_context_counts', (len(raw_model), len(clean_model)) == (68068, 67961))
check('raw_punctuation_contexts', sum(any(t is not None and lm.is_punct(t) for t in key) for key in raw_model) == 8187)
check('nonfinal_periods', sum(t == '.' for s in raw for t in s[:-1]) == 37)
check('punctuation_initial_training_sentences', sum(lm.is_punct(s[0]) for s in raw) == 25)
check('sentence_initial_bigrams', Counter(tuple(s[:2]) for s in raw).most_common(3) ==
      [(('It', 'is'), 158), (('We', 'have'), 102), (('We', 'will'), 77)])

import string
filtered = [t for t in tokens if t not in string.punctuation]
tables = {
    label: {k: Counter(zip(*(words[i:] for i in range(k)))).most_common(10) for k in (1, 2, 3)}
    for label, words in [('kept', tokens), ('filtered', filtered)]
}
answers = (SRC / 'ANSWERS.md').read_text()
rows = [line for line in answers.splitlines() if re.match(r'^\| \d+ \|', line)]
check('ten_frequency_rows', len(rows) == 10)
entries = 0
for line in rows:
    cells = [s.strip() for s in line.strip('|').split('|')]
    rank = int(cells[0])
    for i, cell in enumerate(cells[1:]):
        token, count = re.match(r'^(.*) ([\d,]+)$', cell).groups()
        expected = tables['kept' if i < 3 else 'filtered'][i % 3 + 1][rank - 1]
        check(f'ngram_entry_{rank}_{i}', token == ' '.join(expected[0]) and int(count.replace(',', '')) == expected[1])
        entries += 1

stats = re.findall(
    r'--- 500 sentences, mean length ([\d.]+) tokens, '
    r'verbatim copies of cleaned corpus sentences (\d+)/500 \(([\d.]+)%\), '
    r'start with a capital (\d+)/500 \(([\d.]+)%\), '
    r'end with terminal punctuation (\d+)/500 \(([\d.]+)%\)',
    (SRC / 'output/comparison.txt').read_text())
table = answers.split('| configuration |', 1)[1].split('What each tweak did:', 1)[0]
comparison_rows = [line for line in table.splitlines() if line.startswith('| ') and not line.startswith('|---')]
check('eight_comparison_rows', len(stats) == len(comparison_rows) == 8)
for i, (line, stat) in enumerate(zip(comparison_rows, stats)):
    cells = [s.strip().replace('**', '') for s in line.strip('|').split('|')]
    mean, copies, copy_pct, capital, capital_pct, terminal, terminal_pct = stat
    check(f'comparison_row_{i}', cells[1:] == [mean, f'{copies}/500 ({copy_pct}%)', f'{capital_pct}%', f'{terminal_pct}%'])
    check(f'comparison_percentages_{i}', all(
        f'{int(count)/5:.1f}' == percent for count, percent in
        [(copies, copy_pct), (capital, capital_pct), (terminal, terminal_pct)]))
check('bigram_copy_rate_visible', stats[4][1:3] == ('2', '0.4'))
check('final_terminal_rate_visible', stats[6][-2:] == ('498', '99.6'))
check('length_unit_in_help', 'minimum tokens, including punctuation' in (SRC / 'improved_lm.py').read_text())

outputs = '\n'.join(p.read_text() for p in (SRC / 'output').glob('*.txt'))
quotes = [line[2:].strip() for line in answers.splitlines() if line.startswith('> ') and '…' not in line]
check('full_sentence_quotes_match_outputs', all(quote in outputs for quote in quotes))
seen = {tuple(s) for s in clean}
samples = (SRC / 'output/improved_final.txt').read_text().splitlines()[1:-1]
check('final_samples_pass_length_and_novelty', len(samples) == 20 and all(
    6 <= len(s.split()) <= 30 and tuple(s.split()) not in seen for s in samples))
fresh = json.loads((BASE / 'fresh_setup.json').read_text())
check('isolated_fresh_install', fresh == {'exit_code': 0, 'punkt_tab_installed': True, 'generated_baseline_successfully': True})

changed = [str(p.relative_to(SRC)) for p in sorted(SRC.rglob('*')) if p.is_file() and
           '__pycache__' not in p.parts and p.name != '.DS_Store' and
           (not (BEFORE / p.relative_to(SRC)).exists() or p.read_bytes() != (BEFORE / p.relative_to(SRC)).read_bytes())]
patches = []
for relative in changed:
    before, after = BEFORE / relative, SRC / relative
    patches.extend(difflib.unified_diff(before.read_text().splitlines(True) if before.exists() else [],
                                      after.read_text().splitlines(True),
                                      fromfile='before/' + relative, tofile='after/' + relative))
(BASE / 'changes.diff').write_text(''.join(patches))
result = {'checks_passed': sum(checks.values()), 'checks': checks, 'ngram_entries_verified': entries,
          'comparison_configurations_verified': len(stats), 'unchanged_outputs': unchanged,
          'outputs_with_summary_only_changes': summary_only, 'fresh_setup': fresh, 'changed_files': changed,
          'current_sha256': {relative: hashlib.sha256((SRC / relative).read_bytes()).hexdigest() for relative in changed}}
(BASE / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['checks_passed', 'ngram_entries_verified', 'comparison_configurations_verified', 'fresh_setup', 'changed_files']}))
