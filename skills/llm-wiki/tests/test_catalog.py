"""Run: python3 -m unittest discover -s skills/llm-wiki/tests -v"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/catalog.py'
spec = importlib.util.spec_from_file_location('catalog', SCRIPT)
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'wiki').mkdir()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return target

    def test_add_rename_drafts_filters_and_no_writes(self):
        self.write('wiki/z.md', '# Lone page\nA body-only phrase: 現行判断')
        self.write('wiki/drafts/a.md', '---\nknowledge_status: current\nstatus: promoted\n---\n# Proposal')
        self.write('raw/source.md', '# Not wiki')
        self.write('wiki/.generated/view.md', '# Not knowledge')
        self.write('wiki/other/AGENTS.md', 'another root')
        self.write('wiki/other/wiki/a.md', '# Other root')
        (self.root / 'wiki/link.md').symlink_to(self.root / 'raw/source.md')
        before = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = catalog.catalog(self.root)
        self.assertEqual([p['path'] for p in result['pages']], ['wiki/drafts/a.md', 'wiki/z.md'])
        self.assertEqual(result['pages'][0]['knowledge_status'], 'draft')
        self.assertEqual(result['pages'][1]['knowledge_status'], 'unknown')
        self.assertIsNone(result['pages'][1]['summary'])
        self.assertTrue(result['complete'])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        found = catalog.catalog(self.root, query='現行判断', statuses=['unknown'])
        self.assertEqual((found['total'], found['matched'], found['filtered_out']), (2, 1, 1))
        self.assertEqual(found['filters']['statuses'], ['unknown'])
        (self.root / 'wiki/z.md').rename(self.root / 'wiki/b.md')
        self.write('wiki/a.md', '# New uncommitted page')
        self.assertEqual([p['path'] for p in catalog.catalog(self.root)['pages']],
                         ['wiki/a.md', 'wiki/b.md', 'wiki/drafts/a.md'])

    @unittest.skipIf(catalog.yaml is None, 'PyYAML unavailable; degraded path tested separately')
    def test_yaml_block_scalars_quoted_values_and_invalid_metadata(self):
        self.write('wiki/good.md', '---\ntitle: "Title: YAML"\nsummary: >-\n  Two lines\n  one summary.\nknowledge_status: mixed\nstatus: complete\naliases: ["異なる語", "a: b"]\ntags: [topic]\n---\n# Heading')
        self.write('wiki/bad.md', '---\nsummary: [broken\n---\n# Bad YAML\nStill searchable')
        self.write('wiki/type.md', '---\nsummary: 3\n---\n# Bad type')
        result = catalog.catalog(self.root)
        good = next(p for p in result['pages'] if p['path'].endswith('good.md'))
        self.assertEqual(good['title'], 'Title: YAML')
        self.assertEqual(good['summary'], 'Two lines one summary.')
        self.assertEqual(good['knowledge_status'], 'mixed')
        self.assertEqual(catalog.catalog(self.root, query='異なる語')['matched'], 1)
        self.assertEqual(len(result['diagnostics']), 2)
        self.assertEqual(result['metadata'], 'degraded')
        self.assertEqual(result['total'], 3)
        self.assertEqual(catalog.catalog(self.root, query='Still searchable')['matched'], 1)

    def test_parser_unavailable_keeps_pages_and_heading(self):
        self.write('wiki/a.md', '---\nsummary: Useful\nknowledge_status: current\n---\n# Retained heading\nBody evidence')
        with patch.object(catalog, 'yaml', None):
            result = catalog.catalog(self.root)
        self.assertEqual(result['metadata'], 'degraded')
        self.assertEqual(result['pages'][0]['title'], 'Retained heading')
        self.assertIsNone(result['pages'][0]['summary'])
        self.assertEqual(result['pages'][0]['knowledge_status'], 'unknown')
        self.assertEqual(result['diagnostics'][0]['path'], 'wiki/a.md')
        # -S hides installed packages, exercising the actual CLI capability fallback.
        run = subprocess.run([sys.executable, '-S', str(SCRIPT), str(self.root)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)['matched'], 1)

    def test_read_failure_reports_path_without_dropping_page(self):
        self.write('wiki/a.md', '# Heading')
        with patch.object(Path, 'read_text', side_effect=PermissionError('permission denied')):
            result = catalog.catalog(self.root)
        self.assertFalse(result['complete'])
        self.assertEqual(result['pages'][0]['path'], 'wiki/a.md')
        self.assertEqual(result['errors'][0]['path'], 'wiki/a.md')
        self.assertEqual(result['pages'][0]['knowledge_status'], 'unknown')
        (self.root / 'wiki/a.md').write_bytes(b'\xff')
        self.assertFalse(catalog.catalog(self.root)['complete'])

    def test_listing_error_empty_missing_and_changed_during_read(self):
        self.assertEqual(catalog.catalog(self.root)['total'], 0)
        self.assertFalse(catalog.catalog(self.root / 'missing')['complete'])
        def failed_walk(path, onerror, followlinks):
            onerror(PermissionError(13, 'permission denied', str(path)))
            return iter(())
        with patch.object(catalog.os, 'walk', side_effect=failed_walk):
            result = catalog.catalog(self.root)
        self.assertFalse(result['complete'])
        self.assertTrue(result['errors'])
        self.write('wiki/a.md', '# Heading')
        with patch.object(catalog, 'stamp', side_effect=[(1,), (2,)]):
            self.assertFalse(catalog.catalog(self.root)['complete'])
        with patch.object(catalog, 'inventory', side_effect=[([self.root / 'wiki/a.md'], [], []), ([], [], [])]):
            self.assertFalse(catalog.catalog(self.root)['complete'])

    def test_independent_branches_add_pages_without_central_files(self):
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.STDOUT, text=True)
        git('init', '-b', 'main')
        git('config', 'user.name', 'Catalog Test')
        git('config', 'user.email', 'catalog@example.invalid')
        git('config', 'commit.gpgsign', 'false')
        self.write('AGENTS.md', 'Test root: pages own knowledge.')
        git('add', 'AGENTS.md')
        git('commit', '-m', 'baseline')
        git('switch', '-c', 'x')
        self.write('wiki/x.md', '# X\nIndependent evidence X.')
        git('add', 'wiki/x.md')
        git('commit', '-m', 'add X')
        git('switch', 'main')
        git('switch', '-c', 'y')
        self.write('wiki/y.md', '# Y\nIndependent evidence Y.')
        git('add', 'wiki/y.md')
        git('commit', '-m', 'add Y')
        git('merge', 'x', '--no-edit')
        self.assertEqual(git('diff', '--name-only', 'main..HEAD').splitlines(), ['wiki/x.md', 'wiki/y.md'])
        self.assertEqual([p['path'] for p in catalog.catalog(self.root)['pages']], ['wiki/x.md', 'wiki/y.md'])


if __name__ == '__main__':
    unittest.main()
