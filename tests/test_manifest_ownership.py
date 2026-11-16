import hashlib
import json
import unittest
import test_installer as helpers


class ManifestOwnershipTests(unittest.TestCase):
    setUp = helpers.InstallerTests.setUp
    run_installer = helpers.InstallerTests.run_installer

    def test_unrelated_files_cannot_be_claimed(self):
        for relative in ('README.md', '.agents/jstack/project.json', '.git/config', '.agents/jstack/manifest.json'):
            with self.subTest(relative=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.write_bytes(b'keep')
                before = path.read_bytes()
                manifest = self.root / '.agents/jstack/manifest.json'
                manifest.parent.mkdir(parents=True, exist_ok=True)
                manifest.write_text(json.dumps({'schema': 1, 'files': {relative: {
                    'kind': 'file', 'sha256': hashlib.sha256(before).hexdigest(), 'executable': False}}}))
                protected = path.read_bytes()
                result = self.run_installer('uninstall', ok=False)
                self.assertNotIn('Traceback', result.stderr)
                self.assertEqual(path.read_bytes(), protected)

    def test_noncanonical_manifest_path_is_rejected(self):
        manifest = self.root / '.agents/jstack/manifest.json'
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({'schema': 1, 'files': {'.agents/skills/check/../write/SKILL.md': {
            'kind': 'file', 'sha256': '0' * 64, 'executable': False}}}))
        self.run_installer('uninstall', ok=False)
