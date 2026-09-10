"""Check artifacts from a real skill run, not a simulated agent or wording match.

Give an independent evaluator this task with the skill path and a temporary
output directory: Bootstrap a plain Markdown wiki for a shared office. Ingest
source A (2026-01-01: capacity is 12 desks) and source B (2026-02-01: fire limit
is 10 people). Answer 'How many people can use the office?' without saving the
answer. Perform read-only lint. Then ingest source C (2026-03-01: desks reduced
to 8; fire limit unchanged). Keep source snapshots and copy the whole knowledge
root after each operation to bootstrap/, ingest/, query/, lint/, update/ in the
output directory; put the answer and lint report outside these copies.

Run: python3 skills/llm-wiki/tests/check_workflow.py /temporary/output-directory
The semantic accuracy of the answer and links requires separate human/agent
review. This check only verifies the observable file invariants of that run.
"""
from pathlib import Path
import sys


def files(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def check(output):
    states = {}
    for stage in ('bootstrap', 'ingest', 'query', 'lint', 'update'):
        root = output / stage
        assert root.is_dir(), f'missing stage: {stage}'
        states[stage] = files(root)
        assert 'AGENTS.md' in states[stage], stage
        assert 'index.md' not in states[stage] and 'log.md' not in states[stage], stage
    assert states['ingest'] == states['query'] == states['lint'], 'unsaved query/lint wrote files'
    assert any(p.startswith('wiki/') for p in states['ingest']), 'ingestion produced no pages'
    changes = {p for p in states['ingest'].keys() | states['update'].keys()
               if states['ingest'].get(p) != states['update'].get(p)}
    assert any(p.startswith('wiki/') for p in changes), 'update did not integrate knowledge'
    assert all(p.startswith(('wiki/', 'raw/')) for p in changes), 'page update changed central files'
    for p, body in states['ingest'].items():
        if p.startswith('raw/'):
            assert states['update'].get(p) == body, f'raw changed: {p}'
    print('PASS: bootstrap, ingest, unsaved query, read-only lint, and page update file invariants')


if __name__ == '__main__':
    check(Path(sys.argv[1]))
