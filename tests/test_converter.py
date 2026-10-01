import unittest
from decimal import Decimal

from converter import ConversionError, convert, convert_all, parse_number, unit_keys
from formatter import format_number
from units import CATEGORIES, find_unit

RATES = {"USD": Decimal("1"), "TRY": Decimal("40"), "EUR": Decimal("0.8")}


class TestParseNumber(unittest.TestCase):
    def test_turkish_input(self):
        cases = [
            ("12,5", "12.5"),
            ("1.000", "1000"),
            ("12.345.678", "12345678"),
            ("1.234,5", "1234.5"),
            ("3.5", "3.5"),
            ("1.00", "1.00"),
            ("-1.000", "-1000"),
            ("  42 ", "42"),
            ("1 000", "1000"),
            ("1e3", "1000"),
            ("0", "0"),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(parse_number(text, "tr"), Decimal(expected))

    def test_english_input(self):
        cases = [("12.5", "12.5"), ("1,000", "1000"), ("1,234.5", "1234.5"), ("-0.25", "-0.25")]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(parse_number(text, "en"), Decimal(expected))

    def test_errors(self):
        cases = [
            ("", "empty"),
            ("   ", "empty"),
            ("abc", "invalid"),
            ("1,2,3", "invalid"),
            ("--5", "invalid"),
            ("NaN", "invalid"),
            ("Infinity", "invalid"),
            ("9" * 41, "too_long"),
            ("1e101", "out_of_range"),
            ("1e-101", "out_of_range"),
        ]
        for text, code in cases:
            with self.subTest(text=text):
                with self.assertRaises(ConversionError) as context:
                    parse_number(text, "tr")
                self.assertEqual(context.exception.code, code)


class TestConvert(unittest.TestCase):
    def test_linear_units_are_exact(self):
        cases = [
            ("length", "1", "km", "m", "1000"),
            ("length", "1", "in", "cm", "2.54"),
            ("length", "1", "mi", "m", "1609.344"),
            ("weight", "1", "kg", "g", "1000"),
            ("speed", "36", "kmh", "ms", "10"),
            ("time", "2", "h", "min", "120"),
            ("data", "1", "kb", "byte", "1000"),
            ("data", "1", "kib", "byte", "1024"),
            ("data", "1", "tb", "gib", "931.3225746154785156250"),
        ]
        for category, value, from_key, to_key, expected in cases:
            with self.subTest(category=category, from_key=from_key, to_key=to_key):
                self.assertEqual(convert(category, Decimal(value), from_key, to_key), Decimal(expected))

    def test_same_unit_returns_same_value(self):
        for category, info in CATEGORIES.items():
            if info["kind"] != "linear":
                continue
            for item in info["units"]:
                with self.subTest(category=category, unit=item["key"]):
                    self.assertEqual(convert(category, Decimal("7.5"), item["key"], item["key"]), Decimal("7.5"))

    def test_round_trip(self):
        for category, info in CATEGORIES.items():
            if info["kind"] != "linear":
                continue
            first, second = info["default"]
            with self.subTest(category=category):
                there = convert(category, Decimal("123.456"), first, second)
                back = convert(category, there, second, first)
                self.assertAlmostEqual(back, Decimal("123.456"), places=20)

    def test_temperature(self):
        cases = [
            ("0", "c", "f", "32"),
            ("100", "c", "f", "212"),
            ("-40", "c", "f", "-40"),
            ("0", "c", "k", "273.15"),
            ("0", "k", "c", "-273.15"),
            ("212", "f", "c", "100"),
        ]
        for value, from_key, to_key, expected in cases:
            with self.subTest(value=value, from_key=from_key, to_key=to_key):
                self.assertEqual(convert("temperature", Decimal(value), from_key, to_key), Decimal(expected))

    def test_absolute_zero_is_allowed_but_not_below(self):
        self.assertEqual(convert("temperature", Decimal("-273.15"), "c", "k"), Decimal("0"))
        for value, unit_key in (("-273.16", "c"), ("-1", "k"), ("-460", "f")):
            with self.subTest(value=value, unit=unit_key):
                with self.assertRaises(ConversionError) as context:
                    convert("temperature", Decimal(value), unit_key, "c")
                self.assertEqual(context.exception.code, "below_absolute_zero")

    def test_currency(self):
        self.assertEqual(convert("currency", Decimal("10"), "USD", "TRY", RATES), Decimal("400"))
        self.assertEqual(convert("currency", Decimal("80"), "TRY", "EUR", RATES), Decimal("1.6"))

    def test_currency_without_rates(self):
        for rates in (None, {}, RATES):
            with self.subTest(rates=rates):
                with self.assertRaises(ConversionError) as context:
                    convert("currency", Decimal("1"), "USD", "GBP", rates)
                self.assertEqual(context.exception.code, "no_rates")

    def test_unknown_unit(self):
        with self.assertRaises(ConversionError) as context:
            convert("length", Decimal("1"), "m", "parsec")
        self.assertEqual(context.exception.code, "unknown_unit")

    def test_unit_keys_and_convert_all(self):
        self.assertEqual(unit_keys("currency"), [])
        self.assertEqual(unit_keys("currency", RATES), ["EUR", "TRY", "USD"])
        results = dict(convert_all("length", Decimal("1"), "m"))
        self.assertEqual(set(results), set(unit_keys("length")))
        self.assertEqual(results["cm"], Decimal("100"))


class TestUnits(unittest.TestCase):
    def test_every_category_is_well_formed(self):
        for category, info in CATEGORIES.items():
            with self.subTest(category=category):
                self.assertIn(info["kind"], ("linear", "temperature", "currency"))
                if info["kind"] == "currency":
                    continue
                keys = [item["key"] for item in info["units"]]
                self.assertEqual(len(keys), len(set(keys)), "duplicate unit key")
                for key in info["default"]:
                    self.assertIsNotNone(find_unit(category, key))
                if info["kind"] == "linear":
                    for item in info["units"]:
                        self.assertGreater(item["factor"], 0)


class TestFormatNumber(unittest.TestCase):
    def test_formatting(self):
        cases = [
            (Decimal("1234567.5"), "tr", "1.234.567,5"),
            (Decimal("1234567.5"), "en", "1,234,567.5"),
            (Decimal("0.1") + Decimal("0.2"), "tr", "0,3"),
            (Decimal(1) / Decimal(3), "en", "0.333333333333"),
            (Decimal("100.000"), "tr", "100"),
            (Decimal("-0"), "tr", "0"),
            (Decimal("-2.5"), "en", "-2.5"),
            (Decimal("1e20"), "tr", "1E+20"),
            (Decimal("1.5e-7"), "tr", "1,5E-7"),
            (Decimal("123456789012345678"), "en", "1.23456789012E+17"),
        ]
        for value, lang, expected in cases:
            with self.subTest(value=value, lang=lang):
                self.assertEqual(format_number(value, lang), expected)

    def test_formatted_text_can_be_parsed_back(self):
        values = ["0.5", "1000", "1234567.891", "-42.125", "1e20", "3e-9", "999999999999"]
        for lang in ("tr", "en"):
            for text in values:
                with self.subTest(lang=lang, value=text):
                    value = Decimal(text)
                    self.assertEqual(parse_number(format_number(value, lang), lang), value)


if __name__ == "__main__":
    unittest.main()
