import unittest
import test_seo_setup as helpers

seo = helpers.seo


class SEODestinationTests(unittest.TestCase):
    setUp = helpers.SEOSetupTests.setUp
    invoke = helpers.SEOSetupTests.invoke

    def test_file_parent_is_rejected_by_dry_run_before_staging(self):
        collision = self.root / '.cursor/skills'
        collision.parent.mkdir()
        collision.write_text('user content')
        with self.assertRaisesRegex(ValueError, 'parent is not a directory'):
            self.invoke('--dry-run')
        self.assertEqual(collision.read_text(), 'user content')
        self.assertFalse((self.root / '.agents').exists())

    def test_alias_parent_inside_destination_is_rejected_before_writes(self):
        provider = self.root / '.claude'
        provider.mkdir()
        (provider / 'skills').symlink_to('../.agents/skills/claude-seo/skills', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'overlap'):
            self.invoke('--dry-run')
        self.assertFalse((self.root / '.agents').exists())

    def test_alias_parent_inside_staging_is_rejected_before_writes(self):
        provider = self.root / '.claude'
        provider.mkdir()
        (provider / 'skills').symlink_to('../.agents/skills/claude-seo.jstack-stage', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'overlap'):
            self.invoke()
        self.assertFalse((self.root / '.agents').exists())

    def test_existing_stage_is_reported_in_dry_run_and_preserved(self):
        stage = self.root / (seo.DEST + '.jstack-stage')
        stage.mkdir(parents=True)
        (stage / 'user.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'staging directory exists'):
            self.invoke('--dry-run')
        self.assertEqual((stage / 'user.txt').read_text(), 'keep')
        self.assertFalse((self.root / seo.DEST).exists())

    def test_whole_directory_discovery_links_remain_supported(self):
        canonical = self.root / '.agents/skills'
        canonical.mkdir(parents=True)
        provider = self.root / '.claude'
        provider.mkdir()
        (provider / 'skills').symlink_to('../.agents/skills', target_is_directory=True)
        self.assertEqual(self.invoke(), 0)
        self.assertTrue((provider / 'skills/seo/SKILL.md').is_file())
