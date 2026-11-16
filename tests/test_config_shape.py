import json
import unittest
import test_installer as helpers


class ConfigShapeTests(unittest.TestCase):
    setUp = helpers.InstallerTests.setUp
    run_installer = helpers.InstallerTests.run_installer

    def test_non_object_config_blocks_all_actions_without_changes(self):
        self.run_installer()
        config = self.root / '.agents/jstack/project.json'
        manifest = self.root / '.agents/jstack/manifest.json'
        before = manifest.read_bytes()
        for value in ([], None, 'text', 42, True):
            config.write_text(json.dumps(value))
            for action in ('install', 'check', 'uninstall'):
                with self.subTest(value=value, action=action):
                    result = self.run_installer(action, ok=False)
                    self.assertIn('JSON object', result.stderr)
                    self.assertEqual(manifest.read_bytes(), before)
                    self.assertEqual(json.loads(config.read_text()), value)

    def test_unknown_object_settings_are_preserved(self):
        config = self.root / '.agents/jstack/project.json'
        config.parent.mkdir(parents=True)
        config.write_bytes(b'{"custom": {"anything": [1, 2]}}\n')
        self.run_installer()
        self.assertEqual(config.read_bytes(), b'{"custom": {"anything": [1, 2]}}\n')
