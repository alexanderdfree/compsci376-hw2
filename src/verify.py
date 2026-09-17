"""Check the current HW2 write-up, corpus, outputs, and instructor examples.

Usage: python src/verify.py
Run from any directory. Results go to the ignored .review-work/ directory.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import string
import sys

ROOT = Path(__file__).resolve().parent.parent
RESULT = ROOT / '.review-work' / 'verification.json'
CONFIGURATIONS = [
    ('uniform', 2, 'keep', 1, 'inf', False),
    ('frequent', 2, 'keep', 1, 'inf', False),
    ('boundary', 2, 'keep', 1, 'inf', False),
    ('boundary', 2, 'strip', 1, 'inf', False),
    ('boundary', 1, 'keep', 1, 'inf', False),
    ('boundary', 3, 'keep', 1, 'inf', False),
    ('boundary', 2, 'keep', 6, '30', True),
    ('boundary', 1, 'keep', 6, '30', True),
]


class VerificationError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def check_files(manifest, group, directory, suffix):
    expected = manifest[group]
    actual = {str(p.relative_to(ROOT)) for p in (ROOT / directory).glob('*' + suffix)}
    require(actual == set(expected), f'{directory}/ file inventory differs from the manifest.')
    for name, digest in expected.items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                f'Checksum mismatch: {name}. See docs/SETUP.md before changing expected values.')
    return len(expected)


def verify():
    import nltk
    from corpus_config import corpus, CORPUS_NAME
    import improved_lm as lm

    manifest = json.loads((ROOT / 'docs/verification.json').read_text())
    expected = manifest['corpus']
    files = corpus.fileids()
    tokens = list(corpus.words())
    sentences = [list(s) for s in corpus.sents()]
    identity = (CORPUS_NAME, len(files), len(tokens), len(sentences), files[0], files[-1])
    recorded = (expected['name'], expected['files'], expected['tokens'], expected['sentences'],
                expected['first_file'], expected['last_file'])
    require(identity == recorded,
            f'Corpus differs from the verified data: expected {recorded}, found {identity}. '
            'Check the environment and data version in docs/SETUP.md.')

    instructor_count = check_files(manifest, 'instructor_sha256', 'originals', '.py')
    output_count = check_files(manifest, 'output_sha256', 'output', '.txt')
    cleaned = lm.clean_sentences(sentences, 'keep')
    raw_model = lm.build_model(sentences, 2)
    clean_model = lm.build_model(cleaned, 2)
    measured = {
        'raw_contexts': len(raw_model),
        'clean_contexts': len(clean_model),
        'raw_punctuation_contexts': sum(any(t is not None and lm.is_punct(t) for t in key)
                                        for key in raw_model),
        'nonfinal_periods': sum(t == '.' for s in sentences for t in s[:-1]),
        'punctuation_initial_sentences': sum(lm.is_punct(s[0]) for s in sentences),
    }
    require(measured == manifest['counts'], 'Context or punctuation counts differ from the verified data.')
    require(Counter(tuple(s[:2]) for s in sentences).most_common(3) ==
            [(('It', 'is'), 158), (('We', 'have'), 102), (('We', 'will'), 77)],
            'The sentence-initial bigram counts differ from the write-up.')

    writeup = (ROOT / 'README.md').read_text()
    frequency_rows = [line for line in writeup.splitlines() if re.match(r'^\| \d+ \|', line)]
    require(len(frequency_rows) == 10, 'Expected ten ranked rows in the n-gram table.')
    filtered = [t for t in tokens if t not in string.punctuation]
    distributions = [Counter(zip(*(words[i:] for i in range(order)))).most_common(10)
                     for words in (tokens, filtered) for order in (1, 2, 3)]
    for rank, line in enumerate(frequency_rows):
        cells = [s.strip() for s in line.strip('|').split('|')]
        require(len(cells) == 7 and cells[0] == str(rank + 1),
                f'Malformed n-gram table row {rank + 1}.')
        for column, cell in enumerate(cells[1:]):
            match = re.fullmatch(r'(.*) ([\d,]+)', cell)
            require(match is not None, f'Malformed n-gram cell at row {rank + 1}, column {column + 1}.')
            gram, count = distributions[column][rank]
            require(match[1] == ' '.join(gram) and int(match[2].replace(',', '')) == count,
                    f'N-gram mismatch at row {rank + 1}, column {column + 1}.')

    marker = '| configuration |'
    require(marker in writeup and 'What each tweak did:' in writeup,
            'The experiment comparison table is missing from README.md.')
    table = writeup.split(marker, 1)[1].split('What each tweak did:', 1)[0]
    comparison_rows = [line for line in table.splitlines() if line.startswith('| ')]
    blocks = (ROOT / 'output/comparison.txt').read_text().strip().split('\n\n')
    require(len(comparison_rows) == len(blocks) == len(CONFIGURATIONS),
            'Expected eight comparison configurations in the write-up and output.')
    summary_pattern = (
        r'--- (\d+) sentences, mean length ([\d.]+) tokens, '
        r'verbatim copies of cleaned corpus sentences (\d+)/(\d+) \(([\d.]+)%\), '
        r'start with a capital (\d+)/(\d+) \(([\d.]+)%\), '
        r'end with terminal punctuation (\d+)/(\d+) \(([\d.]+)%\), rejected .*'
    )
    for index, (line, block, config) in enumerate(zip(comparison_rows, blocks, CONFIGURATIONS), 1):
        header, summary = block.splitlines()
        fields = dict(part.split('=', 1) for part in header.split())
        start, context, punct, minimum, maximum, novel = config
        required = {'corpus': CORPUS_NAME, 'start': start, 'context': str(context), 'punct': punct,
                    'min_len': str(minimum), 'max_len': maximum, 'novel': str(novel),
                    'seed': str(manifest['seed'])}
        require(all(fields.get(key) == value for key, value in required.items()),
                f'Configuration mismatch in comparison row {index}.')
        match = re.fullmatch(summary_pattern, summary)
        require(match is not None, f'Malformed summary in comparison row {index}.')
        n, mean, copies, copy_n, copy_pct, capital, capital_n, capital_pct, terminal, terminal_n, terminal_pct = match.groups()
        require(int(n) == manifest['comparison_sentences'] and n == copy_n == capital_n == terminal_n,
                f'Wrong sample size in comparison row {index}.')
        for count, percent in [(copies, copy_pct), (capital, capital_pct), (terminal, terminal_pct)]:
            require(0 <= int(count) <= int(n) and f'{100 * int(count) / int(n):.1f}' == percent,
                    f'Percentage mismatch in comparison row {index}.')
        cells = [s.strip().replace('**', '') for s in line.strip('|').split('|')]
        require(len(cells) == 5 and cells[1:] ==
                [mean, f'{copies}/{n} ({copy_pct}%)', f'{capital_pct}%', f'{terminal_pct}%'],
                f'Write-up does not match saved comparison row {index}.')

    output_text = '\n'.join(p.read_text() for p in (ROOT / 'output').glob('*.txt'))
    quotes = [line.lstrip()[2:].strip() for line in writeup.splitlines()
              if line.lstrip().startswith('> ') and '…' not in line]
    require(bool(quotes) and all(quote in output_text for quote in quotes),
            'A complete quoted sample is missing from the saved outputs.')
    final_lines = (ROOT / 'output/improved_final.txt').read_text().splitlines()[1:-1]
    seen = {tuple(s) for s in cleaned}
    trained_trigrams = {gram for s in cleaned for gram in zip(s, s[1:], s[2:])}
    require(len(final_lines) == manifest['sample_sentences'], 'Wrong number of final sample sentences.')
    for index, line in enumerate(final_lines, 1):
        words = tuple(line.split())
        require(6 <= len(words) <= 30 and words not in seen,
                f'Final sample {index} violates the length or novelty constraint.')
        require(all(gram in trained_trigrams for gram in zip(words, words[1:], words[2:])),
                f'Final sample {index} contains a trigram absent from the cleaned corpus.')

    return {'status': 'passed', 'environment': {'python': sys.version.split()[0], 'nltk': nltk.__version__},
            'corpus': {'files': len(files), 'sentences': len(sentences), 'tokens': len(tokens)},
            'ngram_entries_verified': 60, 'comparison_configurations_verified': len(CONFIGURATIONS),
            'complete_quotations_verified': len(quotes), 'final_samples_verified': len(final_lines),
            'outputs_verified': output_count, 'instructor_examples_verified': instructor_count}


def main():
    try:
        result = verify()
    except (VerificationError, OSError, ValueError, KeyError, LookupError, ImportError) as error:
        result = {'status': 'failed', 'error': str(error),
                  'help': 'See docs/SETUP.md for dependencies, data provenance, and reproduction commands.'}
    RESULT.parent.mkdir(exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
