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

    def test_external_metadata_symlinks_are_not_read(self):
        outside = self.root.parent / 'private.json'
        outside.write_text('{"secret": "must not appear"}')
        for relative in ('package.json', '.agents/jstack/project.json', '.agents/jstack/manifest.json'):
            with self.subTest(relative=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(outside)
                result, report = self.report()
                self.assertEqual(result.returncode, 1)
                self.assertIn('escapes the project', report['error'])
                self.assertNotIn('secret', result.stdout)
                path.unlink()

    def test_internal_metadata_symlink_is_supported(self):
        target = self.root / 'project-package.json'
        target.write_text('{"scripts": {"test": "python3 -m unittest"}}')
        (self.root / 'package.json').symlink_to(target.name)
        _, report = self.report()
        self.assertEqual(report['package_scripts'], {'test': 'python3 -m unittest'})
