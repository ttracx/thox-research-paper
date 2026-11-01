"""Offline tests. These are not host-routing, live-connector or publication tests."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'skills/thox-research-paper'
SCRIPT = PAPER / 'scripts/research_context.py'
spec = importlib.util.spec_from_file_location('research_context', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ResearchContextTests(unittest.TestCase):
    def new(self):
        return m.checkpoint('test-project', 'Synthetic integration fixture')

    def codes(self, obj):
        return m.validate_checkpoint(obj)['errors']

    def test_both_authors(self):
        self.assertEqual([a['name'] for a in m.publication_authors()], ['Craig Ross', 'Tommy Xaypanya'])

    def test_tommy_profile(self):
        a = m.publication_authors()[1]
        self.assertEqual(a['position'], 'Chief Technology Officer and Co-Founder')
        self.assertEqual(a['affiliation'], 'THOX.ai LLC')
        self.assertEqual(a['orcid'], '0009-0000-4425-9565')

    def test_craig_profile(self):
        a = m.publication_authors()[0]
        self.assertEqual(a['position'], 'Chief Executive Officer')
        self.assertIsNone(a['orcid'])

    def test_json_authors(self):
        self.assertEqual(len(json.loads(m.render_authors('json'))['authors']), 2)

    def test_markdown_authors(self):
        text = m.render_authors('markdown')
        self.assertIn('Craig Ross', text)
        self.assertIn('Tommy Xaypanya', text)
        self.assertIn('Chief Technology Officer and Co-Founder', text)

    def test_tex_authors(self):
        text = m.render_authors('tex')
        self.assertTrue(text.startswith('\\author{'))
        self.assertIn('Craig Ross', text)
        self.assertIn('Tommy Xaypanya', text)
        self.assertIn('0009-0000-4425-9565', text)

    def test_tex_escape(self):
        self.assertEqual(m.tex_escape('a_b & 10%'), r'a\_b \& 10\%')

    def test_public_fields_allowlist(self):
        profile = m.author_profile()
        profile['default_authors'][0]['account_name'] = 'synthetic-not-for-export'
        with patch.object(m, 'author_profile', return_value=profile):
            self.assertNotIn('synthetic-not-for-export', m.render_authors('json'))

    def test_new_checkpoint_private(self):
        obj = self.new()
        self.assertEqual(obj['classification'], 'private-draft')
        self.assertEqual(obj['stage'], 'intake')
        self.assertFalse(obj['publication']['ready'])
        self.assertFalse(obj['publication']['submitted'])

    def test_new_checkpoint_not_remote(self):
        self.assertEqual(self.new()['connection']['status'], 'STUDIO_NOT_CONNECTED')

    def test_valid_checkpoint(self):
        report = m.validate_checkpoint(self.new())
        self.assertTrue(report['structurally_valid'])
        self.assertFalse(report['publication_ready'])

    def test_missing_craig_fails(self):
        obj = self.new(); obj['authors'].pop(0)
        self.assertIn('DEFAULT_AUTHOR_MISSING', self.codes(obj))

    def test_missing_tommy_fails(self):
        obj = self.new(); obj['authors'].pop(1)
        self.assertIn('DEFAULT_AUTHOR_MISSING', self.codes(obj))

    def test_profile_mismatch(self):
        obj = self.new(); obj['authors'][1]['orcid'] = '0000-0000-0000-0000'
        self.assertIn('AUTHOR_PROFILE_MISMATCH', self.codes(obj))

    def test_preserve_extra_author(self):
        obj = self.new(); obj['authors'].append({'id': 'fixture-coauthor', 'name': 'Synthetic Test Fixture'})
        self.assertTrue(m.validate_checkpoint(obj)['structurally_valid'])

    def test_preserve_changed_order(self):
        obj = self.new(); obj['authors'].reverse()
        self.assertTrue(m.validate_checkpoint(obj)['structurally_valid'])

    def test_duplicate_author_fails(self):
        obj = self.new(); obj['authors'].append(obj['authors'][0])
        self.assertIn('DUPLICATE_AUTHORS', self.codes(obj))

    def test_invalid_project_id(self):
        with self.assertRaises(ValueError): m.checkpoint('../escape', 'fixture')

    def test_invalid_topic(self):
        with self.assertRaises(ValueError): m.checkpoint('fixture', '  ')

    def test_revision_boolean_rejected(self):
        obj = self.new(); obj['revision'] = True
        self.assertIn('INVALID_REVISION', self.codes(obj))

    def test_stage_rejected(self):
        obj = self.new(); obj['stage'] = 'published'
        self.assertIn('INVALID_STAGE', self.codes(obj))

    def test_refinement_bound(self):
        obj = self.new(); obj['refinement']['completed_cycles'] = 6
        self.assertIn('INVALID_REFINEMENT_BOUND', self.codes(obj))

    def test_profile_migration(self):
        obj = self.new(); obj['author_profile_version'] = '0.0.0'
        self.assertIn('AUTHOR_PROFILE_MIGRATION_REQUIRED', self.codes(obj))

    def test_remote_receipt_required(self):
        obj = self.new(); obj['connection']['status'] = 'STUDIO_VERIFIED'
        self.assertIn('CONNECTION_RECEIPT_REQUIRED', self.codes(obj))

    def test_claimed_readiness_not_certified(self):
        obj = self.new(); obj['publication']['ready'] = True
        self.assertFalse(m.validate_checkpoint(obj)['publication_ready'])

    def test_malformed_object(self):
        self.assertFalse(m.validate_checkpoint([])['structurally_valid'])
        self.assertFalse(m.validate_checkpoint({})['structurally_valid'])

    def test_malformed_author(self):
        obj = self.new(); obj['authors'] = [None]
        self.assertIn('INVALID_AUTHORS', self.codes(obj))

    def test_author_id_object(self):
        obj = self.new(); obj['authors'][0]['id'] = {}
        self.assertIn('INVALID_AUTHOR_ID', self.codes(obj))

    def test_cli_roundtrip(self):
        result = subprocess.run([sys.executable, str(SCRIPT), 'checkpoint', '--project-id', 'fixture', '--topic', 'Fixture'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'checkpoint.json'; path.write_text(result.stdout)
            checked = subprocess.run([sys.executable, str(SCRIPT), 'validate-checkpoint', str(path)], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0)
        self.assertFalse(json.loads(checked.stdout)['publication_ready'])

    def test_cli_does_not_write_files(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([sys.executable, str(SCRIPT), 'authors'], cwd=d, capture_output=True, check=True)
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_cli_bad_json_no_echo(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'bad.json'; path.write_text('synthetic-private-value')
            result = subprocess.run([sys.executable, str(SCRIPT), 'validate-checkpoint', str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('synthetic-private-value', result.stdout + result.stderr)

    def test_implicit_configuration(self):
        for skill in ['thox-research-paper', 'thox-research-studio']:
            folder = ROOT/'skills'/skill
            self.assertIn('allow_implicit_invocation: true', (folder/'agents/openai.yaml').read_text())
            self.assertIn('description: Automatically', (folder/'SKILL.md').read_text())

    def test_manifest_consistency(self):
        a = json.loads((ROOT/'plugin.json').read_text())
        b = json.loads((ROOT/'.codex-plugin/plugin.json').read_text())
        self.assertEqual(a['name'], b['name'])
        self.assertEqual(a['version'], '1.2.0')
        self.assertEqual(a['version'], b['version'])
        self.assertEqual(a['extensions']['com.openai']['interface'], b['interface'])
        self.assertNotIn('mcpServers', a)
        self.assertNotIn('mcpServers', b)

    def test_existing_preflight_preserved(self):
        self.assertTrue((PAPER/'scripts/arxiv_preflight.py').is_file())
        text = (PAPER/'SKILL.md').read_text()
        self.assertIn('references/arxiv-preflight.md', text)
        self.assertIn('references/arxiv-account-workflow.md', text)

    def test_no_account_in_public_author_profile(self):
        text = (PAPER/'references/publication-authors.json').read_text()
        self.assertNotIn('account_name', text)
        self.assertNotIn('password', text)


if __name__ == '__main__':
    unittest.main()
