"""Pure path-name regressions; runnable directly without app/pytest fixtures."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "device_alias_path_security",
    Path(__file__).resolve().parents[1] / "backend/core/path_security.py",
)
path_security = importlib.util.module_from_spec(spec)
spec.loader.exec_module(path_security)


class WindowsDeviceAliases(unittest.TestCase):
    def test_superscript_devices(self):
        for prefix in ("COM", "LPT", "com", "lpt"):
            for digit in ("\u00b9", "\u00b2", "\u00b3"):
                for suffix in ("", ".wav", ".part.wav"):
                    name = prefix + digit + suffix
                    with self.subTest(name=name):
                        self.assertEqual(path_security.portable_filename(name), "_" + name)
                        with self.assertRaises(path_security.UnsafePath):
                            path_security.safe_filename(name)

    def test_ordinary_names(self):
        for name in ("COM0.wav", "COM10.wav", "LPT4notes.wav", "voice\u00b2.wav"):
            with self.subTest(name=name):
                self.assertEqual(path_security.portable_filename(name), name)
                self.assertEqual(path_security.safe_filename(name), name)


if __name__ == "__main__":
    unittest.main()
