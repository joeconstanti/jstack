"""Refresh imported skills twice while the jstack source version stays fixed."""
import argparse
from contextlib import contextmanager
import json
import shutil
import subprocess
import unittest
from unittest.mock import patch

import install
import test_seo_setup as helpers
import upstream


class ImportRefreshTests(unittest.TestCase):
    setUp = helpers.SEOSetupTests.setUp
    invoke = helpers.SEOSetupTests.invoke

    def refresh(self, dry_run=False, refresh_imports=True):
        args = argparse.Namespace(action='install', project=str(self.root),
                                  dry_run=dry_run, refresh_imports=refresh_imports)
        with patch.object(upstream, 'checkout', self.checkout):
            return install.run(args)

    @contextmanager
    def checkout(self, repo, commit=None):
        if repo == upstream.MATT_REPO:
            yield self.matt, self.revision
        elif commit == upstream.SEO_PIN:
            yield self.upstream, commit
        else:
            yield self.latest_seo, self.revision

    def test_same_jstack_release_refreshes_both_sources_and_preserves_runtime(self):
        self.assertEqual(install.run(argparse.Namespace(
            action='install', project=str(self.root), dry_run=False)), 0)
        manifest_path = self.root / install.MANIFEST
        previous = json.loads(manifest_path.read_text())
        previous['version'] = '0.5.0'
        manifest_path.write_text(json.dumps(previous))
        self.assertEqual(self.invoke(), 0)
        seo_root = self.root / upstream.SEO_DEST
        runtime = seo_root / 'runtime-state.json'
        runtime.write_text('local state')
        self.matt = self.base / 'matt'
        (self.matt / 'skills').mkdir(parents=True)
        (self.matt / 'LICENSE').write_text('Upstream license')
        for relative in upstream.MATT_SKILLS.values():
            path = self.matt / 'skills' / relative
            path.mkdir(parents=True)
            (path / 'SKILL.md').write_text(f'---\nname: {relative.split("/")[-1]}\n---\nInitial text\n')
        self.latest_seo = self.base / 'latest-seo'
        shutil.copytree(self.upstream, self.latest_seo)
        subprocess.run(['git', 'init', '-q', str(self.latest_seo)], check=True)
        (self.latest_seo / '.gitignore').write_text('*-REPORT.md\n')
        (self.latest_seo / 'skills/seo/template-REPORT.md').write_text('Report template')
        seo_source = self.latest_seo / 'skills/seo/SKILL.md'
        grill_source = self.matt / 'skills/productivity/grill-me/SKILL.md'
        grill = self.root / '.agents/skills/grill/SKILL.md'
        seo_skill = seo_root / 'skills/seo/SKILL.md'

        self.revision = 'a' * 40
        seo_source.write_text('# Updated SEO')
        bundled_grill = grill.read_text()
        self.assertEqual(self.refresh(dry_run=True, refresh_imports=False), 0)
        self.assertEqual(grill.read_text(), bundled_grill)
        self.assertEqual(seo_skill.read_text(), f'# SEO {upstream.SEO_DEST}')
        self.assertEqual(self.refresh(refresh_imports=False), 0)
        self.assertIn('name: grill\n', grill.read_text())
        self.assertEqual(seo_skill.read_text(), '# Updated SEO')
        self.assertIn('!/skills/seo/template-REPORT.md', (seo_root / '.gitignore').read_text())

        self.revision = 'b' * 40
        grill_source.write_text(grill_source.read_text().replace('Initial text', 'New text'))
        seo_source.write_text('# New SEO')
        seo_skill.write_text('local edit')
        with self.assertRaisesRegex(ValueError, 'managed file changed'):
            self.refresh()
        self.assertNotIn('New text', grill.read_text())
        self.assertEqual(seo_skill.read_text(), 'local edit')

        seo_skill.write_text('# Updated SEO')
        self.assertEqual(self.refresh(), 0)
        self.assertIn('New text', grill.read_text())
        self.assertEqual(seo_skill.read_text(), '# New SEO')
        self.assertEqual(runtime.read_text(), 'local state')
        manifest = json.loads((self.root / install.MANIFEST).read_text())
        self.assertEqual(set(manifest['upstream'].values()), {self.revision})
        self.assertEqual(install.run(argparse.Namespace(
            action='uninstall', project=str(self.root), dry_run=False)), 0)
        self.assertEqual(seo_skill.read_text(), '# New SEO')
