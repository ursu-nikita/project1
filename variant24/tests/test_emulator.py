"""Unittests for variant 24 shell emulator."""
import base64
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from emulator import Emulator, ShellError, load_vfs, normalize

ROOT = pathlib.Path(__file__).resolve().parents[1]


class EmulatorTests(unittest.TestCase):
    """Test commands, parser, and nonpersistent modifications."""

    def setUp(self):
        """Load a fresh virtual filesystem for each test."""
        document, checksum = load_vfs(ROOT / 'vfs/sample.json')
        self.shell = Emulator(document, checksum)

    def test_ls_cd_and_quoted_arguments(self):
        """Directory changes and quoted path parsing work."""
        self.assertIn('home', self.shell.execute('ls'))
        self.shell.execute('cd "home/student/docs"')
        self.assertEqual(self.shell.cwd, '/home/student/docs')
        self.assertEqual(self.shell.execute('ls'), 'data.txt')

    def test_tac(self):
        """Reverse line order is correct."""
        self.assertEqual(self.shell.execute('tac readme.txt'),
                         'line three\nline two\nline one')

    def test_chmod_in_memory(self):
        """Mode changes do not alter the original JSON file."""
        original = (ROOT / 'vfs/sample.json').read_bytes()
        self.shell.execute('chmod 600 readme.txt')
        self.assertEqual(self.shell.node('readme.txt')['mode'], '600')
        self.assertEqual((ROOT / 'vfs/sample.json').read_bytes(), original)

    def test_errors(self):
        """Invalid commands, file types, and argument counts fail."""
        for command in ('unexpected', 'ls a b', 'cd readme.txt',
                        'chmod 999 readme.txt', 'tac home', 'ls "bad'):
            with self.subTest(command=command):
                with self.assertRaises(ShellError):
                    self.shell.execute(command)

    def test_information(self):
        """Metadata contains name and a 64-character SHA-256 hash."""
        output = self.shell.execute('vfs-info')
        self.assertIn('Name: sample', output)
        self.assertIn('SHA-256: ', output)
        self.assertEqual(len(output.split('SHA-256: ')[1]), 64)

    def test_exit(self):
        """Exit stops the shell loop."""
        self.shell.execute('exit')
        self.assertFalse(self.shell.running)


if __name__ == '__main__':
    unittest.main()
