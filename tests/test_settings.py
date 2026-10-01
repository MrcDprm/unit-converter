import tempfile
import unittest
from pathlib import Path
from unittest import mock

import storage
from settings import SETTINGS_FILE, clean_settings, load_settings, save_settings


class TempDataDir(unittest.TestCase):
    """Testler gerçek kullanıcı klasörüne değil geçici bir klasöre yazar."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        patcher = mock.patch.object(storage, "DATA_DIR", Path(self.temp.name))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.temp.cleanup)


class TestSettings(TempDataDir):
    def test_defaults(self):
        self.assertEqual(load_settings(), {"lang": "tr", "theme": "dark", "category": "length", "units": {}})

    def test_save_and_load(self):
        settings = {"lang": "en", "theme": "light", "category": "currency", "units": {"currency": ["EUR", "TRY"]}}
        save_settings(settings)
        self.assertEqual(load_settings(), settings)

    def test_invalid_values_fall_back(self):
        data = {
            "lang": "de",
            "theme": "pink",
            "category": "magic",
            "units": {"length": ["m"], "weight": ["kg", 5], "magic": ["a", "b"], "time": ["h", "min"]},
        }
        self.assertEqual(
            clean_settings(data),
            {"lang": "tr", "theme": "dark", "category": "length", "units": {"time": ["h", "min"]}},
        )

    def test_broken_file(self):
        (Path(self.temp.name) / SETTINGS_FILE).write_text("not json", encoding="utf-8")
        self.assertEqual(load_settings()["lang"], "tr")


if __name__ == "__main__":
    unittest.main()
