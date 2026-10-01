import io
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

import storage
from currency import (
    CACHE_FILE,
    MAX_RESPONSE_BYTES,
    REFRESH_AFTER_SECONDS,
    RatesError,
    fetch_rates,
    get_rates,
    parse_rates,
)

CODES = ["USD", "TRY", "EUR", "GBP", "CHF", "JPY", "CNY", "RUB", "SAR", "AED", "AZN"]


def api_response(**changes):
    data = {
        "result": "success",
        "base_code": "USD",
        "time_last_update_unix": 1_790_000_000,
        "rates": {code: 1 if code == "USD" else 2.5 for code in CODES},
    }
    data.update(changes)
    return data


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def opener_returning(body):
    return lambda request, timeout: FakeResponse(body)


class TempDataDir(unittest.TestCase):
    """Testler gerçek kullanıcı klasörüne değil geçici bir klasöre yazar."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        patcher = mock.patch.object(storage, "DATA_DIR", Path(self.temp.name))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.temp.cleanup)


class TestParseRates(unittest.TestCase):
    def test_valid_response(self):
        result = parse_rates(api_response())
        self.assertEqual(result["rates"]["USD"], Decimal("1"))
        self.assertEqual(result["rates"]["TRY"], Decimal("2.5"))
        self.assertEqual(result["updated"], 1_790_000_000)

    def test_bad_entries_are_skipped(self):
        rates = api_response()["rates"]
        rates.update({"usd": 3, "TOOLONG": 3, "XXX": True, "YYY": "5", "ZZZ": -1, "QQQ": 0, "BIG": 1e13})
        result = parse_rates(api_response(rates=rates))
        self.assertEqual(set(result["rates"]), set(CODES))

    def test_invalid_responses(self):
        cases = [
            None,
            [],
            api_response(result="error"),
            api_response(base_code="EUR"),
            api_response(rates=None),
            api_response(time_last_update_unix="yesterday"),
            api_response(time_last_update_unix=True),
            api_response(rates={"USD": 1, "TRY": 40}),
            api_response(rates={code: 2 for code in CODES}),
        ]
        for data in cases:
            with self.subTest(data=data):
                with self.assertRaises(RatesError):
                    parse_rates(data)


class TestFetchRates(unittest.TestCase):
    def test_reads_json(self):
        body = json.dumps(api_response()).encode()
        result = fetch_rates(opener_returning(body))
        self.assertEqual(result["rates"]["TRY"], Decimal("2.5"))

    def test_rejects_invalid_json(self):
        with self.assertRaises(RatesError):
            fetch_rates(opener_returning(b"<html>not json</html>"))

    def test_rejects_too_large_response(self):
        with self.assertRaises(RatesError):
            fetch_rates(opener_returning(b" " * (MAX_RESPONSE_BYTES + 1)))


class TestGetRates(TempDataDir):
    NOW = 1_800_000_000

    def fail(self):
        raise OSError("no connection")

    def test_downloads_and_caches(self):
        result, status = get_rates(now=self.NOW, fetch=lambda: parse_rates(api_response()))
        self.assertEqual(status, "fresh")
        self.assertEqual(result["rates"]["TRY"], Decimal("2.5"))
        self.assertTrue((Path(self.temp.name) / CACHE_FILE).exists())

    def test_recent_cache_avoids_download(self):
        get_rates(now=self.NOW, fetch=lambda: parse_rates(api_response()))
        result, status = get_rates(now=self.NOW + 60, fetch=self.fail)
        self.assertEqual(status, "cached")
        self.assertEqual(result["rates"]["TRY"], Decimal("2.5"))

    def test_old_cache_is_used_when_offline(self):
        get_rates(now=self.NOW, fetch=lambda: parse_rates(api_response()))
        result, status = get_rates(now=self.NOW + REFRESH_AFTER_SECONDS + 1, fetch=self.fail)
        self.assertEqual(status, "offline")
        self.assertEqual(result["rates"]["TRY"], Decimal("2.5"))

    def test_unavailable_without_cache_or_connection(self):
        self.assertEqual(get_rates(now=self.NOW, fetch=self.fail), (None, "unavailable"))

    def test_corrupted_cache_is_ignored(self):
        (Path(self.temp.name) / CACHE_FILE).write_text("{broken", encoding="utf-8")
        self.assertEqual(get_rates(now=self.NOW, fetch=self.fail), (None, "unavailable"))

    def test_cache_from_the_future_is_refreshed(self):
        get_rates(now=self.NOW, fetch=lambda: parse_rates(api_response()))
        _, status = get_rates(now=self.NOW - 3600, fetch=lambda: parse_rates(api_response()))
        self.assertEqual(status, "fresh")


if __name__ == "__main__":
    unittest.main()
