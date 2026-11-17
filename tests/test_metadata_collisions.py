import json
import unittest
import test_installer as helpers


class MetadataCollisionTests(unittest.TestCase):
    setUp = helpers.InstallerTests.setUp
    run_installer = helpers.InstallerTests.run_installer

    def test_dangling_config_alias_into_managed_content_is_rejected(self):
        config = self.root / '.agents/jstack/project.json'
        config.parent.mkdir(parents=True)
        config.symlink_to('../skills/check/SKILL.md')
        for extra in (('--dry-run',), ()):
            with self.subTest(extra=extra):
                result = self.run_installer('install', *extra, ok=False)
                self.assertIn('metadata', result.stderr)
                self.assertTrue(config.is_symlink())
                self.assertFalse((self.root / '.agents/skills').exists())
                self.assertFalse((config.parent / 'manifest.json').exists())

    def test_dangling_config_alias_to_managed_parent_is_rejected(self):
        config = self.root / '.agents/jstack/project.json'
        config.parent.mkdir(parents=True)
        config.symlink_to('../skills/check')
        self.run_installer(ok=False)
        self.assertFalse((self.root / '.agents/skills').exists())

    def test_unrelated_internal_config_link_is_retained(self):
        settings = self.root / 'settings.json'
        settings.write_text('{"main_branch":"trunk"}')
        config = self.root / '.agents/jstack/project.json'
        config.parent.mkdir(parents=True)
        config.symlink_to('../../settings.json')
        self.run_installer()
        self.run_installer('check')
        self.run_installer('uninstall')
        self.assertTrue(config.is_symlink())
        self.assertEqual(json.loads(settings.read_text()), {'main_branch': 'trunk'})

    def test_dangling_manifest_alias_into_managed_content_is_rejected(self):
        manifest = self.root / '.agents/jstack/manifest.json'
        manifest.parent.mkdir(parents=True)
        manifest.symlink_to('../skills/check/SKILL.md')
        result = self.run_installer(ok=False)
        self.assertIn('metadata', result.stderr)
        self.assertTrue(manifest.is_symlink())
        self.assertFalse((self.root / '.agents/skills').exists())
