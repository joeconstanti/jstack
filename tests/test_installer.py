import json
import importlib.util
import contextlib
import io
from unittest.mock import patch
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

SOURCE = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project with spaces'
        self.root.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)

    def run_installer(self, action='install', *extra, ok=True):
        result = subprocess.run([sys.executable, str(SOURCE / 'install.py'), action, '--project', str(self.root), *extra], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def test_roundtrip_config_and_unrelated_files(self):
        unrelated = self.root / '.claude/skills/existing/SKILL.md'
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text('user skill')
        self.run_installer()
        for provider in ['.agents', '.claude', '.cursor', '.gemini', '.opencode']:
            self.assertTrue((self.root / provider / 'skills/pull/SKILL.md').is_file())
        self.assertEqual((self.root / '.agents/jstack/rules.md').read_bytes(), (SOURCE / 'shared/rules.md').read_bytes())
        config = self.root / '.agents/jstack/project.json'
        config.write_text('{"site_url":"https://example.com"}\n')
        manifest_before = (self.root / '.agents/jstack/manifest.json').read_bytes()
        self.run_installer()
        self.run_installer('check')
        self.assertEqual((self.root / '.agents/jstack/manifest.json').read_bytes(), manifest_before)
        self.assertIn('example.com', config.read_text())
        self.run_installer('uninstall')
        self.assertFalse((self.root / '.agents/skills/pull/SKILL.md').exists())
        self.assertTrue(config.is_file())
        self.assertEqual(unrelated.read_text(), 'user skill')

    def test_dry_run_has_no_filesystem_changes(self):
        self.run_installer('install', '--dry-run')
        self.assertFalse((self.root / '.agents').exists())

    def test_collision_prevents_partial_install(self):
        collision = self.root / '.cursor/commands/verify.md'
        collision.parent.mkdir(parents=True)
        collision.write_text('existing command')
        self.run_installer(ok=False)
        self.assertEqual(collision.read_text(), 'existing command')
        self.assertFalse((self.root / '.agents').exists())

    def test_modified_files_block_update_and_uninstall(self):
        self.run_installer()
        skill = self.root / '.agents/skills/pull/SKILL.md'
        skill.write_text('my custom version')
        self.run_installer(ok=False)
        self.run_installer('uninstall', ok=False)
        self.run_installer('check', ok=False)
        self.assertEqual(skill.read_text(), 'my custom version')

    def test_whole_directory_discovery_links(self):
        canonical = self.root / '.agents/skills'
        canonical.mkdir(parents=True)
        for provider in ['.claude', '.cursor', '.gemini']:
            folder = self.root / provider
            folder.mkdir()
            (folder / 'skills').symlink_to('../.agents/skills', target_is_directory=True)
        self.run_installer()
        self.run_installer('check')
        self.assertFalse((canonical / 'pull').is_symlink())
        self.assertTrue((self.root / '.claude/skills/pull/SKILL.md').is_file())
        self.run_installer('uninstall')
        self.assertTrue((self.root / '.claude/skills').is_symlink())

    def test_external_parent_symlink_is_rejected(self):
        outside = Path(self.temp.name) / 'global'
        outside.mkdir()
        (self.root / '.agents').symlink_to(outside, target_is_directory=True)
        self.run_installer(ok=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_external_leaf_symlink_is_rejected(self):
        outside = Path(self.temp.name) / 'global'
        outside.mkdir()
        alias = self.root / '.claude/skills/pull'
        alias.parent.mkdir(parents=True)
        alias.symlink_to(outside, target_is_directory=True)
        self.run_installer(ok=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_provider_specific_whole_directory_link(self):
        folder = self.root / '.agents/providers/claude/skills'
        folder.mkdir(parents=True)
        (self.root / '.claude').mkdir()
        (self.root / '.claude/skills').symlink_to('../.agents/providers/claude/skills', target_is_directory=True)
        self.run_installer()
        self.run_installer('check')
        self.assertTrue((folder / 'edit/SKILL.md').is_file())

    def test_generated_gemini_commands_parse_and_keep_arguments(self):
        self.run_installer()
        for command in (self.root / '.gemini/commands').glob('*.toml'):
            data = tomllib.loads(command.read_text())
            self.assertIn('{{args}}', data['prompt'])
            self.assertIn('.agents/jstack/rules.md', data['prompt'])

    def test_uninstalled_check_fails(self):
        self.run_installer('check', ok=False)

    def test_non_repository_is_rejected(self):
        other = Path(self.temp.name) / 'not-a-repo'
        other.mkdir()
        result = subprocess.run([sys.executable, str(SOURCE / 'install.py'), 'install', '--project', str(other)], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(other.iterdir()), [])

    def test_filesystem_failure_rolls_back_written_files(self):
        spec = importlib.util.spec_from_file_location('jstack_install', SOURCE / 'install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = module.atomic_write
        calls = []
        def fail_second(path, data, executable=False):
            calls.append(path)
            if len(calls) == 2:
                raise OSError('simulated disk write failure')
            return original(path, data, executable)
        import argparse
        with contextlib.redirect_stdout(io.StringIO()), patch.object(module, 'atomic_write', side_effect=fail_second):
            with self.assertRaises(OSError):
                module.run(argparse.Namespace(action='install', project=str(self.root), dry_run=False))
        self.assertFalse((self.root / '.agents/jstack/manifest.json').exists())
        self.assertEqual([p for p in self.root.rglob('*') if p.is_file() and '.git' not in p.parts], [])

    def test_existing_seo_is_retained_without_network(self):
        skill = self.root / '.agents/skills/seo/SKILL.md'
        skill.parent.mkdir(parents=True)
        skill.write_text('project-owned SEO')
        result = subprocess.run([sys.executable, str(SOURCE / 'setup-seo.py'), '--project', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(skill.read_text(), 'project-owned SEO')
        self.assertFalse((self.root / '.agents/skills/claude-seo').exists())

    def test_skill_catalog_has_valid_frontmatter_and_references(self):
        names = {'pull', 'audit', 'edit', 'preview', 'pr', 'push', 'check', 'review', 'verify', 'doctor', 'update-skills'}
        self.assertEqual({p.name for p in (SOURCE / 'skills').iterdir()}, names)
        for name in names:
            text = (SOURCE / 'skills' / name / 'SKILL.md').read_text()
            frontmatter = text.split('---', 2)[1]
            self.assertIn(f'name: {name}\n', frontmatter)
            description = next(line for line in frontmatter.splitlines() if line.startswith('description: '))
            self.assertGreater(len(json.loads(description.removeprefix('description: '))), 20)
            self.assertNotIn('[TODO', text)
            # Shared rules live once in rules.md; each skill points there and stays short.
            self.assertIn('Read `.agents/jstack/rules.md` first', text)
            self.assertLessEqual(len(text.splitlines()), 60, name)
            # Publishing and self-update fire only when typed, in Claude/Cursor and Codex alike.
            typed_only = 'disable-model-invocation: true' in frontmatter
            policy = SOURCE / 'skills' / name / 'agents/openai.yaml'
            self.assertEqual(typed_only, name in {'push', 'update-skills'}, name)
            self.assertEqual(typed_only, policy.is_file() and 'allow_implicit_invocation: false' in policy.read_text(), name)
            # No skill can invoke a typed-only skill, so none may tell the agent to.
            for typed in ('push', 'update-skills'):
                self.assertNotRegex(text, rf'(run|use|invoke) the {typed} skill', name)


if __name__ == '__main__':
    unittest.main()
