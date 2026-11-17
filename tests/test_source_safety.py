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

    def test_shared_release_inputs_cannot_be_links(self):
        import shutil
        from pathlib import Path
        for relative in ('LICENSE', 'VERSION', 'shared/rules.md', 'shared'):
            with self.subTest(relative=relative):
                source = self.copy_source()
                for name in ('LICENSE', 'VERSION', 'shared'):
                    origin = helpers.SOURCE / name
                    if origin.is_dir():
                        shutil.copytree(origin, source / name)
                    else:
                        shutil.copy2(origin, source / name)
                target = source / relative
                outside = source.parent / ('outside-' + relative.replace('/', '-'))
                target.rename(outside)
                target.symlink_to(outside, target_is_directory=outside.is_dir())
                with self.assertRaisesRegex(ValueError, 'source symlink'):
                    load_installer(source).plan(Path(self.temp_root(source)))

    @staticmethod
    def temp_root(source):
        root = source.parent / 'target'
        root.mkdir(exist_ok=True)
        return root.resolve()
