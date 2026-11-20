import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import test_installer as helpers


class ValidateCLITests(unittest.TestCase):
    def test_validate_requires_no_project_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(helpers.SOURCE / 'install.py'), 'validate'],
                                    cwd=temp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report['ok'])
            self.assertIn('push', report['skills'])
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_invalid_catalog_is_rejected_by_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp)
            for name in ('install.py', 'upstream.py', 'VERSION', 'LICENSE'):
                shutil.copy2(helpers.SOURCE / name, source)
            shutil.copytree(helpers.SOURCE / 'shared', source / 'shared')
            shutil.copytree(helpers.SOURCE / 'skills', source / 'skills')
            (source / 'skills/check/SKILL.md').write_text('invalid')
            result = subprocess.run([sys.executable, str(source / 'install.py'), 'validate'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('frontmatter', result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertFalse((source / '.agents').exists())

    def test_empty_release_cannot_remove_existing_installation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'release'
            source.mkdir()
            for name in ('install.py', 'upstream.py', 'VERSION', 'LICENSE'):
                shutil.copy2(helpers.SOURCE / name, source)
            shutil.copytree(helpers.SOURCE / 'shared', source / 'shared')
            (source / 'skills').mkdir()
            project = root / 'project'
            subprocess.run(['git', 'init', '-q', str(project)], check=True)
            target = ['--project', str(project)]
            subprocess.run([sys.executable, str(helpers.SOURCE / 'install.py'), 'install', *target],
                           capture_output=True, check=True)
            for arguments in (['validate'], ['install', *target, '--dry-run'], ['install', *target]):
                with self.subTest(arguments=arguments):
                    result = subprocess.run([sys.executable, str(source / 'install.py'), *arguments],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1, result.stdout)
                    self.assertIn('catalog is empty', result.stderr)
            subprocess.run([sys.executable, str(helpers.SOURCE / 'install.py'), 'check', *target],
                           capture_output=True, check=True)

    def test_validate_checks_required_release_files(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp)
            shutil.copy2(helpers.SOURCE / 'install.py', source)
            shutil.copy2(helpers.SOURCE / 'upstream.py', source)
            for name in ('VERSION', 'LICENSE'):
                shutil.copy2(helpers.SOURCE / name, source)
            shutil.copytree(helpers.SOURCE / 'skills', source / 'skills')
            shutil.copytree(helpers.SOURCE / 'shared', source / 'shared')
            rules = source / 'shared/rules.md'
            rules.unlink()
            command = [sys.executable, str(source / 'install.py'), 'validate']
            missing = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(missing.returncode, 1)
            self.assertIn('Missing source file: shared/rules.md', missing.stderr)
            rules.symlink_to('../LICENSE')
            linked = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(linked.returncode, 1)
            self.assertIn('Unsafe source symlink: shared/rules.md', linked.stderr)

    def test_install_still_requires_explicit_target(self):
        result = subprocess.run([sys.executable, str(helpers.SOURCE / 'install.py'), 'install'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('--project is required', result.stderr)
