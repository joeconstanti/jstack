"""Offline pinned-checkout fixtures: no upstream network or runtime setup."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('seo_setup', SOURCE / 'setup-seo.py')
seo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo)


class SEOSetupTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.root = self.base / 'project'
        self.root.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.upstream = self.base / 'upstream'
        for relative, data in {
            'skills/seo/SKILL.md': '# SEO ${CLAUDE_PLUGIN_ROOT}',
            'scripts/launcher.py': '# instructions only',
            'LICENSE': 'Fixture license', 'README.md': 'Fixture source',
            'requirements.txt': '', '.gitignore': 'runtime/',
            '.claude-plugin/plugin.json': '{}',
        }.items():
            path = self.upstream / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data, encoding='utf-8')

    def invoke(self, *extra):
        real_run = subprocess.run
        def run(command, **kwargs):
            if command[:2] == ['git', 'clone']:
                shutil.copytree(self.upstream, command[-1], symlinks=True)
                return subprocess.CompletedProcess(command, 0)
            if len(command) > 3 and command[3] == 'checkout':
                return subprocess.CompletedProcess(command, 0)
            return real_run(command, **kwargs)
        with patch.object(seo.subprocess, 'run', side_effect=run), \
             patch.object(seo.subprocess, 'check_output', return_value=seo.COMMIT + '\n'), \
             patch.object(sys, 'argv', ['setup-seo.py', '--project', str(self.root), *extra]):
            return seo.main()

    def test_plain_source_installs_license_and_discovery_without_runtime(self):
        self.assertEqual(self.invoke(), 0)
        destination = self.root / seo.DEST
        self.assertEqual((destination / 'LICENSE').read_text(), 'Fixture license')
        self.assertFalse(json.loads((destination / 'JSTACK-INSTALL.json').read_text())['runtime_setup'])
        for provider in ('.agents', '.claude', '.cursor', '.gemini', '.opencode'):
            self.assertTrue((self.root / provider / 'skills/seo/SKILL.md').is_file())

    def test_linked_upstream_content_is_rejected_before_writes(self):
        for relative in ('skills/seo/SKILL.md', 'scripts', 'LICENSE', '.claude-plugin'):
            with self.subTest(relative=relative):
                path = self.upstream / relative
                outside = self.base / ('external-' + relative.replace('/', '-'))
                path.rename(outside)
                path.symlink_to(outside, target_is_directory=outside.is_dir())
                try:
                    with self.assertRaisesRegex(ValueError, 'source symlink'):
                        self.invoke()
                    self.assertFalse((self.root / '.agents').exists())
                finally:
                    path.unlink()
                    outside.rename(path)
                    for provider in ('.agents', '.claude', '.cursor', '.gemini', '.opencode'):
                        shutil.rmtree(self.root / provider, ignore_errors=True)

    def test_broken_upstream_link_is_rejected_in_dry_run(self):
        (self.upstream / 'skills/seo/broken').symlink_to('absent')
        with self.assertRaisesRegex(ValueError, 'source symlink'):
            self.invoke('--dry-run')
        self.assertFalse((self.root / '.agents').exists())
