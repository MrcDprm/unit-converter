"""Dönüşüm mantığı: doğrusal birimler katsayıyla, sıcaklık formülle, döviz kurla çevrilir.

Arayüzden bağımsızdır; bütün fonksiyonlar Decimal alır ve Decimal döndürür, test edilir.
"""
import re
from decimal import Decimal, InvalidOperation

from units import CATEGORIES, find_unit

ABSOLUTE_ZERO_C = Decimal("-273.15")
MAX_INPUT_LENGTH = 40
MAX_EXPONENT = 100  # 10^100'den büyük ya da 10^-100'den küçük sayılar reddedilir
TR_GROUPED = re.compile(r"[-+]?\d{1,3}(\.\d{3})+")  # "1.000", "12.345.678"


class ConversionError(ValueError):
    """Kullanıcıya gösterilecek hata. code, i18n'deki mesajın anahtarıdır."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


def parse_number(text, lang="tr"):
    """Kullanıcının yazdığı metni sayıya çevirir.

    Türkçede virgül ondalık, nokta binlik ayırıcıdır ("1.234,5" → 1234.5, "1.000" → 1000);
    virgül yoksa ve noktalar üçerli gruplar değilse nokta ondalık sayılır ("3.5").
    İngilizcede virgül binlik, nokta ondalık ayırıcıdır ("1,234.5").
    """
    cleaned = text.strip().replace(" ", "")
    if not cleaned:
        raise ConversionError("empty")
    if len(cleaned) > MAX_INPUT_LENGTH:
        raise ConversionError("too_long")
    if lang == "en":
        cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif TR_GROUPED.fullmatch(cleaned):
        cleaned = cleaned.replace(".", "")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise ConversionError("invalid") from None
    if not value.is_finite():  # "NaN", "Infinity" gibi yazımlar
        raise ConversionError("invalid")
    if value != 0 and abs(value.adjusted()) > MAX_EXPONENT:
        raise ConversionError("out_of_range")
    return value


def to_celsius(value, unit_key):
    if unit_key == "c":
        return value
    if unit_key == "f":
        return (value - 32) * 5 / 9
    return value + ABSOLUTE_ZERO_C  # kelvin


def from_celsius(value, unit_key):
    if unit_key == "c":
        return value
    if unit_key == "f":
        return value * 9 / 5 + 32
    return value - ABSOLUTE_ZERO_C  # kelvin


def convert(category, value, from_key, to_key, rates=None):
    """value'yu from_key biriminden to_key birimine çevirir.

    rates sadece döviz için gerekir: {"USD": 1, "TRY": 49.01, ...} (1 USD'nin karşılıkları).
    """
    kind = CATEGORIES[category]["kind"]

    if kind == "temperature":
        celsius = to_celsius(value, from_key)
        if celsius < ABSOLUTE_ZERO_C:
            raise ConversionError("below_absolute_zero")
        return from_celsius(celsius, to_key)

    if kind == "currency":
        if not rates or from_key not in rates or to_key not in rates:
            raise ConversionError("no_rates")
        return value / rates[from_key] * rates[to_key]

    source = find_unit(category, from_key)
    target = find_unit(category, to_key)
    if source is None or target is None:
        raise ConversionError("unknown_unit")
    return value * source["factor"] / target["factor"]


def unit_keys(category, rates=None):
    """Kategorideki birimlerin anahtarları; döviz için kurlardaki para birimleri."""
    if CATEGORIES[category]["kind"] == "currency":
        return sorted(rates) if rates else []
    return [item["key"] for item in CATEGORIES[category]["units"]]


def convert_all(category, value, from_key, rates=None):
    """"Tüm birimler" tablosu için: değerin kategorideki her birimdeki karşılığı."""
    return [(key, convert(category, value, from_key, key, rates)) for key in unit_keys(category, rates)]
