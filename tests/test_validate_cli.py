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
            shutil.copy2(helpers.SOURCE / 'install.py', source)
            shutil.copytree(helpers.SOURCE / 'skills', source / 'skills')
            (source / 'skills/check/SKILL.md').write_text('invalid')
            result = subprocess.run([sys.executable, str(source / 'install.py'), 'validate'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('frontmatter', result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertFalse((source / '.agents').exists())

    def test_install_still_requires_explicit_target(self):
        result = subprocess.run([sys.executable, str(helpers.SOURCE / 'install.py'), 'install'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('--project is required', result.stderr)
