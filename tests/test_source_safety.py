import unittest
import test_spec_limits as helpers

load_installer = helpers.load_installer


class SourceSafetyTests(unittest.TestCase):
    copy_source = helpers.SpecLimitTests.copy_source

    def test_external_source_file_is_rejected(self):
        source = self.copy_source()
        (source / 'skills/check/leak.txt').symlink_to('/etc/hosts')
        with self.assertRaisesRegex(ValueError, 'source symlink'):
            load_installer(source).validate_catalog()

    def test_broken_source_link_is_rejected(self):
        source = self.copy_source()
        (source / 'skills/check/missing').symlink_to('absent')
        with self.assertRaisesRegex(ValueError, 'source symlink'):
            load_installer(source).validate_catalog()

    def test_source_directory_link_is_rejected(self):
        source = self.copy_source()
        (source / 'skills/check/linked').symlink_to(source / 'skills/write', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'source symlink'):
            load_installer(source).validate_catalog()
