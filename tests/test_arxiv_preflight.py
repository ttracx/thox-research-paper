"""Synthetic, credential-free fixtures for the offline preflight checker."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/thox-research-paper/scripts/arxiv_preflight.py'
spec = importlib.util.spec_from_file_location('preflight', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.write('main.tex', r'\documentclass{article}\begin{document}Example.\end{document}')

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, path, text):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)

    def report(self, **kw):
        return module.audit(self.root, kw.get('source_format', 'tex'), kw.get('main', 'main.tex'))

    def codes(self, field='errors'):
        return {x['code'] for x in self.report()[field]}

    def test_clean_source_passes_static_only(self):
        r = self.report()
        self.assertTrue(r['static_checks_passed'])
        self.assertFalse(r['publication_ready'])
        self.assertTrue(r['manual_checks_required'])

    def test_pdf_only_cannot_claim_tex(self):
        (self.root / 'main.tex').unlink()
        self.write('main.pdf', '%PDF-1.7 synthetic fixture')
        r = self.report(main='main.pdf')
        self.assertIn('TEX_SOURCE_REQUIRED', {x['code'] for x in r['errors']})

    def test_missing_main(self):
        self.assertFalse(self.report(main='absent.tex')['static_checks_passed'])

    def test_hidden_directory(self):
        self.write('.git/config', 'synthetic')
        self.assertIn('UNSAFE_DIRECTORY', self.codes())

    def test_hidden_file(self):
        self.write('.env', 'synthetic')
        self.assertIn('UNSAFE_FILE', self.codes())

    def test_secret_value_not_echoed(self):
        self.write('main.tex', 'password=synthetic-fixture-only')
        r = self.report()
        self.assertIn('POSSIBLE_SECRET', {x['code'] for x in r['errors']})
        self.assertNotIn('synthetic-fixture-only', json.dumps(r))

    def test_comment_review(self):
        self.write('main.tex', 'Content % internal note')
        self.assertIn('TEX_COMMENT_REVIEW', self.codes('warnings'))

    def test_escaped_percent(self):
        self.write('main.tex', r'Rate is 10\% today.')
        self.assertNotIn('TEX_COMMENT_REVIEW', self.codes('warnings'))

    def test_terminal_percent(self):
        self.write('main.tex', 'Content%')
        self.assertNotIn('TEX_COMMENT_REVIEW', self.codes('warnings'))

    def test_double_slash_then_percent(self):
        self.write('main.tex', r'Line\\% internal note')
        self.assertIn('TEX_COMMENT_REVIEW', self.codes('warnings'))

    def test_missing_include(self):
        self.write('main.tex', r'\input{missing}')
        self.assertIn('MISSING_INCLUDED_FILE', self.codes())

    def test_present_include(self):
        self.write('main.tex', r'\input{sections/method}')
        self.write('sections/method.tex', 'Method')
        self.assertTrue(self.report()['static_checks_passed'])

    def test_path_escape(self):
        self.write('main.tex', r'\input{../outside}')
        self.assertIn('UNRESOLVED_OR_UNSAFE_INCLUDE', self.codes())

    def test_missing_bibliography(self):
        self.write('main.tex', r'\bibliography{refs}')
        self.assertIn('MISSING_BIBLIOGRAPHY', self.codes())

    def test_bib_supported(self):
        self.write('main.tex', r'\bibliography{refs}')
        self.write('refs.bib', '@article{fixture,title={Example}}')
        self.assertTrue(self.report()['static_checks_passed'])

    def test_bbl_supported(self):
        self.write('main.tex', r'\bibliography{refs}')
        self.write('main.bbl', r'\begin{thebibliography}{1}\end{thebibliography}')
        self.assertTrue(self.report()['static_checks_passed'])

    def test_symlink(self):
        (self.root / 'linked.tex').symlink_to(self.root / 'main.tex')
        self.assertIn('UNSAFE_FILE', self.codes())

    def test_case_collision(self):
        self.write('Main.tex', 'Other')
        self.assertIn('CASE_COLLISION', self.codes())

    def test_build_file_rejected(self):
        self.write('main.log', 'synthetic')
        self.assertIn('BUILD_ARTIFACT', self.codes())

    def test_cookie_file_rejected(self):
        self.write('cookies.json', '{}')
        self.assertIn('PRIVATE_FILE', self.codes())

    def test_hash_changes(self):
        before = self.report()['inventory_sha256']
        self.write('main.tex', 'Changed')
        self.assertNotEqual(before, self.report()['inventory_sha256'])

    def test_hash_stable(self):
        self.assertEqual(self.report()['inventory_sha256'], self.report()['inventory_sha256'])

    def test_main_path_escape(self):
        self.assertFalse(self.report(main='../main.tex')['static_checks_passed'])

    def test_shell_escape(self):
        self.write('main.tex', r'\immediate\write18{echo synthetic}')
        self.assertIn('SHELL_ESCAPE_DIRECTIVE', self.codes())

    def test_invalid_main_with_bibliography_does_not_crash(self):
        self.write('main.tex', r'\bibliography{refs}')
        self.assertFalse(self.report(main='/')['static_checks_passed'])

    def test_json_secret_not_echoed(self):
        self.write('metadata.json', '{"password":"synthetic-json-fixture"}')
        r = self.report()
        self.assertFalse(r['static_checks_passed'])
        self.assertNotIn('synthetic-json-fixture', json.dumps(r))

    def test_invalid_format(self):
        self.assertFalse(self.report(source_format='unknown')['static_checks_passed'])


if __name__ == '__main__':
    unittest.main()
