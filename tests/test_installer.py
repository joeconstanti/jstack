import json
import shutil
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

    def test_code_free_project_installs_knowledge_resources_and_adapters(self):
        self.run_installer()
        for name in ('design', 'research', 'write'):
            canonical = self.root / '.agents/skills' / name
            self.assertTrue(list((canonical / 'references').glob('*.md')))
            for provider in ('.claude', '.cursor', '.gemini', '.opencode'):
                self.assertEqual((self.root / provider / 'skills' / name).resolve(), canonical.resolve())
            for provider, suffix in (('.cursor', '.md'), ('.gemini', '.toml'), ('.opencode', '.md')):
                self.assertTrue((self.root / provider / 'commands' / (name + suffix)).is_file())
        self.assertFalse((self.root / 'package.json').exists())
        self.run_installer('check')
        self.run_installer('uninstall')
        for name in ('design', 'research', 'write'):
            self.assertFalse(any(p.is_file() for p in (self.root / '.agents/skills' / name).rglob('*')))

    def test_catalog_expansion_update_preserves_config_and_rejects_new_collision(self):
        # Simulate the preceding catalog, then update via the real CLI.
        old_source = Path(self.temp.name) / 'old-source'
        old_source.mkdir()
        for filename in ('install.py', 'LICENSE', 'VERSION'):
            shutil.copy2(SOURCE / filename, old_source / filename)
        for folder in ('skills', 'shared'):
            shutil.copytree(SOURCE / folder, old_source / folder)
        for name in ('design', 'research', 'write'):
            shutil.rmtree(old_source / 'skills' / name)
        result = subprocess.run([sys.executable, str(old_source / 'install.py'), 'install',
                                 '--project', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        config = self.root / '.agents/jstack/project.json'
        config.write_text('{"main_branch": "trunk"}\n')
        manifest = self.root / '.agents/jstack/manifest.json'
        before = manifest.read_bytes()
        collision = self.root / '.agents/skills/write/SKILL.md'
        collision.parent.mkdir()
        collision.write_text('existing writing skill')
        self.run_installer(ok=False)
        self.assertEqual(manifest.read_bytes(), before)
        self.assertEqual(collision.read_text(), 'existing writing skill')
        self.assertFalse((self.root / '.agents/skills/design').exists())
        collision.unlink()
        collision.parent.rmdir()
        self.run_installer()
        self.run_installer('check')
        self.assertEqual(json.loads(config.read_text()), {'main_branch': 'trunk'})
        self.assertTrue((self.root / '.agents/skills/write/references/editorial.md').is_file())

    def test_adapters_load_canonical_skill_and_keep_arguments(self):
        self.run_installer()
        for name in ('design', 'research', 'write', 'push'):
            for provider in ('.cursor', '.gemini', '.opencode'):
                suffix = '.toml' if provider == '.gemini' else '.md'
                content = (self.root / provider / 'commands' / (name + suffix)).read_text()
                prompt = tomllib.loads(content)['prompt'] if suffix == '.toml' else content
                self.assertIn(f'.agents/skills/{name}/SKILL.md', prompt)
                self.assertIn('{{args}}' if suffix == '.toml' else '$ARGUMENTS', prompt)
                self.assertNotIn('references/', prompt)
                self.assertLess(len(prompt), 350)

    def test_doctor_separates_optional_readiness_from_integrity(self):
        self.run_installer()
        doctor = self.root / '.agents/skills/doctor/scripts/doctor.py'
        def diagnose():
            result = subprocess.run([sys.executable, str(doctor), '--project', str(self.root)],
                                    capture_output=True, text=True)
            return result, json.loads(result.stdout)
        result, report = diagnose()
        self.assertEqual(result.returncode, 0, report)
        self.assertTrue(report['ok'])
        self.assertEqual(report['workflows']['edit']['instructions'], 'missing')
        self.assertEqual(report['workflows']['audit']['runtime'], 'unverified')
        skill = self.root / '.agents/skills/seo/SKILL.md'
        skill.parent.mkdir()
        skill.write_text('project-owned SEO')
        result, report = diagnose()
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report['workflows']['audit']['instructions'], 'available')
        (self.root / '.agents/skills/write/SKILL.md').write_text('modified')
        result, report = diagnose()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any('missing or modified' in item for item in report['problems']))

    def test_malformed_manifests_fail_without_writes_or_tracebacks(self):
        self.run_installer()
        manifest = self.root / '.agents/jstack/manifest.json'
        doctor = self.root / '.agents/skills/doctor/scripts/doctor.py'
        for malformed in ([], {}, {'schema': 2, 'files': {}},
                          {'schema': 1, 'files': []}, {'schema': 1, 'files': {'bad': None}}):
            with self.subTest(manifest=malformed):
                manifest.write_text(json.dumps(malformed))
                before = manifest.read_bytes()
                for action in ('install', 'check', 'uninstall'):
                    result = self.run_installer(action, ok=False)
                    self.assertIn('Invalid', result.stderr)
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertEqual(manifest.read_bytes(), before)
                result = subprocess.run([sys.executable, str(doctor), '--project', str(self.root)],
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(json.loads(result.stdout)['ok'])
                self.assertNotIn('Traceback', result.stderr)

    def test_late_update_failure_restores_all_managed_files(self):
        self.run_installer()
        spec = importlib.util.spec_from_file_location('jstack_install_late', SOURCE / 'install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        def snapshot():
            return {str(p.relative_to(self.root)): module.state(p) for p in self.root.rglob('*')
                    if '.git' not in p.relative_to(self.root).parts and (p.is_file() or p.is_symlink())}
        before = snapshot()
        desired = module.plan(self.root.resolve())
        desired['.agents/jstack/rules.md'] = module.file_entry(b'updated rules')
        desired['.agents/jstack/new-file.md'] = module.file_entry(b'new file')
        original = module.atomic_write
        failed = False
        def fail_manifest(path, data, executable=False):
            nonlocal failed
            if path.name == 'manifest.json' and not failed:
                failed = True
                raise OSError('simulated late failure')
            return original(path, data, executable)
        import argparse
        with contextlib.redirect_stdout(io.StringIO()), patch.object(module, 'plan', return_value=desired), \
                patch.object(module, 'atomic_write', side_effect=fail_manifest):
            with self.assertRaisesRegex(OSError, 'late failure'):
                module.run(argparse.Namespace(action='install', project=str(self.root), dry_run=False))
        self.assertTrue(failed)
        self.assertEqual(snapshot(), before)
        self.run_installer('check')

    def test_invalid_source_catalog_fails_before_target_writes(self):
        spec = importlib.util.spec_from_file_location('jstack_install_catalog', SOURCE / 'install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        catalog = Path(self.temp.name) / 'catalog'
        shutil.copytree(SOURCE / 'skills', catalog / 'skills')
        skill = catalog / 'skills/write/SKILL.md'
        original = skill.read_text()
        policy = catalog / 'skills/push/agents/openai.yaml'
        original_policy = policy.read_text()
        cases = [original.replace('name: write', 'name: different'),
                 original.replace('description: ', 'unknown: '),
                 original.replace('references/editorial.md', 'references/missing.md'),
                 original + '\n' * 61]
        import argparse
        with patch.object(module, 'SOURCE', catalog):
            for content in cases:
                skill.write_text(content)
                with self.assertRaises(ValueError):
                    module.run(argparse.Namespace(action='install', project=str(self.root), dry_run=False))
                self.assertFalse((self.root / '.agents').exists())
            skill.write_text(original)
            policy.write_text(original_policy.replace('false', 'true'))
            with self.assertRaises(ValueError):
                module.run(argparse.Namespace(action='install', project=str(self.root), dry_run=False))
            self.assertFalse((self.root / '.agents').exists())

    def test_skill_catalog_has_valid_frontmatter_and_references(self):
        names = {'pull', 'audit', 'edit', 'preview', 'pr', 'push', 'check', 'review', 'verify', 'doctor', 'update-skills', 'design', 'research', 'write'}
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
