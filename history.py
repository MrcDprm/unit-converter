"""Dönüşüm geçmişi: son 50 dönüşüm kullanıcı klasöründe saklanır.

Değerler metin olarak (Decimal'ın tam yazımıyla) saklanır; ekranda dile göre biçimlendirilir.
Dosyadan okunan kayıtlara güvenilmez: sadece bilinen alanlar ve geçerli değerler alınır.
"""
import re
from decimal import Decimal, InvalidOperation

from storage import load_json, save_json
from units import CATEGORIES

HISTORY_FILE = "history.json"
MAX_ENTRIES = 50
UNIT_KEY = re.compile(r"[A-Za-z0-9_]{1,20}")
MAX_NUMBER_LENGTH = 60


def make_entry(category, value, from_key, to_key, result):
    return {"category": category, "value": str(value), "from": from_key, "to": to_key, "result": str(result)}


def _is_number(text):
    if not isinstance(text, str) or len(text) > MAX_NUMBER_LENGTH:
        return False
    try:
        return Decimal(text).is_finite()
    except InvalidOperation:
        return False


def is_entry(item):
    return (
        isinstance(item, dict)
        and item.get("category") in CATEGORIES
        and all(isinstance(item.get(key), str) and UNIT_KEY.fullmatch(item[key]) for key in ("from", "to"))
        and _is_number(item.get("value"))
        and _is_number(item.get("result"))
    )


def clean_entry(item):
    """Sadece bilinen alanlar kopyalanır; dosyaya elle eklenmiş fazladan alanlar atılır."""
    return {key: item[key] for key in ("category", "value", "from", "to", "result")}


def load_history():
    data = load_json(HISTORY_FILE, [])
    if not isinstance(data, list):
        return []
    return [clean_entry(item) for item in data if is_entry(item)][:MAX_ENTRIES]


def add_entry(history, entry):
    """Yeni dönüşümü başa ekler. Aynı dönüşüm (kategori, değer, birimler) zaten varsa yukarı taşınır."""
    same = lambda item: all(item[key] == entry[key] for key in ("category", "value", "from", "to"))
    return [entry, *[item for item in history if not same(item)]][:MAX_ENTRIES]


def save_history(history):
    save_json(HISTORY_FILE, history)