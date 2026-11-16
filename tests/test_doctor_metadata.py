import json
import subprocess
import sys
import unittest
import test_installer as helpers

DOCTOR = helpers.SOURCE / 'skills/doctor/scripts/doctor.py'


class DoctorMetadataTests(unittest.TestCase):
    setUp = helpers.InstallerTests.setUp

    def report(self):
        result = subprocess.run([sys.executable, str(DOCTOR), '--project', str(self.root)],
                                capture_output=True, text=True)
        self.assertNotIn('Traceback', result.stderr)
        return result, json.loads(result.stdout)

    def test_metadata_shapes_return_structured_errors(self):
        for relative in ('package.json', '.agents/jstack/project.json', '.agents/jstack/manifest.json'):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            for value in ('[]', 'null', '"text"', '{'):
                with self.subTest(relative=relative, value=value):
                    path.write_text(value)
                    result, report = self.report()
                    self.assertEqual(result.returncode, 1)
                    self.assertFalse(report['ok'])
                    self.assertIn('error', report)
            path.unlink()

    def test_scripts_must_be_an_object(self):
        (self.root / 'package.json').write_text('{"scripts": ["npm test"]}')
        result, report = self.report()
        self.assertEqual(result.returncode, 1)
        self.assertIn('scripts', report['error'])
