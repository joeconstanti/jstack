import json
import os
import subprocess
import sys
import unittest
import test_installer as helpers


class UTF8Tests(unittest.TestCase):
    setUp = helpers.InstallerTests.setUp

    def test_non_ascii_config_under_ascii_locale(self):
        config = self.root / '.agents/jstack/project.json'
        config.parent.mkdir(parents=True)
        config.write_text('{"client": "café £"}', encoding='utf-8')
        before = config.read_bytes()
        env = {**os.environ, 'LC_ALL': 'C', 'PYTHONUTF8': '0', 'PYTHONCOERCECLOCALE': '0'}
        commands = [
            [str(helpers.SOURCE / 'install.py'), 'install'],
            [str(helpers.SOURCE / 'install.py'), 'check'],
            [str(helpers.SOURCE / 'skills/doctor/scripts/doctor.py')],
        ]
        for command in commands:
            result = subprocess.run([sys.executable, *command, '--project', str(self.root)],
                                    env=env, capture_output=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout)['project_config']['client'], 'café £')
        self.assertEqual(config.read_bytes(), before)
