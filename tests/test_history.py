import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

import storage
from history import HISTORY_FILE, MAX_ENTRIES, add_entry, load_history, make_entry, save_history


def entry(value="1", from_key="m", to_key="ft", result="3.28"):
    return make_entry("length", Decimal(value), from_key, to_key, Decimal(result))


class TempDataDir(unittest.TestCase):
    """Testler gerçek kullanıcı klasörüne değil geçici bir klasöre yazar."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        patcher = mock.patch.object(storage, "DATA_DIR", Path(self.temp.name))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.temp.cleanup)

    def write(self, name, data):
        (Path(self.temp.name) / name).write_text(json.dumps(data), encoding="utf-8")


class TestAddEntry(unittest.TestCase):
    def test_newest_first(self):
        history = add_entry(add_entry([], entry("1")), entry("2"))
        self.assertEqual([item["value"] for item in history], ["2", "1"])

    def test_duplicate_moves_to_top(self):
        history = [entry("2"), entry("1")]
        history = add_entry(history, entry("1"))
        self.assertEqual([item["value"] for item in history], ["1", "2"])

    def test_limit(self):
        history = []
        for number in range(MAX_ENTRIES + 10):
            history = add_entry(history, entry(str(number)))
        self.assertEqual(len(history), MAX_ENTRIES)
        self.assertEqual(history[0]["value"], str(MAX_ENTRIES + 9))


class TestStoredHistory(TempDataDir):
    def test_save_and_load(self):
        history = [entry("12.5"), entry("1", "kg", "lb")]
        history[1]["category"] = "weight"
        save_history(history)
        self.assertEqual(load_history(), history)

    def test_missing_or_broken_file(self):
        self.assertEqual(load_history(), [])
        (Path(self.temp.name) / HISTORY_FILE).write_text("[{", encoding="utf-8")
        self.assertEqual(load_history(), [])
        self.write(HISTORY_FILE, {"not": "a list"})
        self.assertEqual(load_history(), [])

    def test_invalid_entries_are_dropped(self):
        good = entry()
        self.write(HISTORY_FILE, [
            good,
            {**good, "category": "magic"},
            {**good, "value": "NaN"},
            {**good, "value": "abc"},
            {**good, "result": "9" * 100},
            {**good, "from": "<script>"},
            {**good, "to": 5},
            "text",
            None,
        ])
        self.assertEqual(load_history(), [good])

    def test_extra_fields_are_removed(self):
        self.write(HISTORY_FILE, [{**entry(), "extra": "x" * 1000}])
        self.assertEqual(load_history(), [entry()])


if __name__ == "__main__":
    unittest.main()
