import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]


def load_installer(source):
    spec = importlib.util.spec_from_file_location('jstack_install_limits', SOURCE / 'install.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SOURCE = source
    return module


class SpecLimitTests(unittest.TestCase):
    def copy_source(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        source = Path(temp.name) / 'jstack'
        shutil.copytree(SOURCE / 'skills', source / 'skills')
        return source

    def test_catalog_respects_specification_limits(self):
        for skill in load_installer(SOURCE).validate_catalog():
            self.assertLessEqual(len(skill.name), 64)

    def test_long_description_is_rejected(self):
        source = self.copy_source()
        skill = source / 'skills/check/SKILL.md'
        text = skill.read_text(encoding='utf-8')
        lines = text.splitlines(keepends=True)
        index = next(i for i, line in enumerate(lines) if line.startswith('description: '))
        lines[index] = 'description: "' + 'x' * 1025 + '"\n'
        skill.write_text(''.join(lines), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '1024'):
            load_installer(source).validate_catalog()


if __name__ == '__main__':
    unittest.main()
