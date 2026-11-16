import unittest
import test_installer as helpers


class ParentCollisionTests(unittest.TestCase):
    setUp = helpers.InstallerTests.setUp
    run_installer = helpers.InstallerTests.run_installer

    def test_file_parent_blocks_install_before_any_write(self):
        provider = self.root / '.opencode'
        provider.mkdir()
        (provider / 'commands').write_bytes(b'keep commands file')
        result = self.run_installer(ok=False)
        self.assertIn('parent is not a directory', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertFalse((self.root / '.agents').exists())
        self.assertEqual((provider / 'commands').read_bytes(), b'keep commands file')

    def test_dry_run_reports_parent_collision(self):
        (self.root / '.gemini').write_bytes(b'keep provider file')
        self.run_installer('install', '--dry-run', ok=False)
        self.assertFalse((self.root / '.agents').exists())
