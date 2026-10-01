"""Döviz kurları: ExchangeRate-API açık erişiminden (anahtarsız) indirilir, doğrulanır ve
kullanıcı klasörüne tarihiyle kaydedilir. İnternet yoksa son kaydedilen kurlar kullanılır.

Kurlar "1 USD kaç birim" biçimindedir: {"USD": 1, "TRY": 49.01, "EUR": 0.88, ...}.
"""
import http.client
import json
import re
import time
import urllib.request
from decimal import Decimal

from app_info import VERSION
from storage import load_json, save_json

API_URL = "https://open.er-api.com/v6/latest/USD"
CACHE_FILE = "rates.json"
TIMEOUT_SECONDS = 8
REFRESH_AFTER_SECONDS = 6 * 60 * 60  # kurlar günde bir güncellenir; 6 saatten yeni kayıt varken istek atılmaz
MAX_RESPONSE_BYTES = 200_000
CURRENCY_CODE = re.compile(r"[A-Z]{3}")
MIN_CURRENCIES = 10


class RatesError(Exception):
    """Kur verisi indirilemedi ya da beklenen biçimde değil."""


def parse_rates(data):
    """API yanıtını (ya da kayıtlı kopyasını) doğrular.

    Dönen sözlük: {"rates": {"USD": Decimal("1"), ...}, "updated": unix zamanı}.
    Beklenmeyen her şeyde RatesError; tek tek bozuk kurlar ise sessizce atlanır.
    """
    if not isinstance(data, dict) or data.get("result") != "success" or data.get("base_code") != "USD":
        raise RatesError("unexpected response")
    raw_rates = data.get("rates")
    updated = data.get("time_last_update_unix")
    if not isinstance(raw_rates, dict) or not isinstance(updated, int) or isinstance(updated, bool):
        raise RatesError("missing fields")

    rates = {}
    for code, value in raw_rates.items():
        # bool, int'in alt sınıfı olduğu için ayrıca elenir (True = 1 kur sayılmasın)
        if isinstance(code, str) and CURRENCY_CODE.fullmatch(code) and isinstance(value, (int, float)) and not isinstance(value, bool):
            if 0 < value < 1e12:
                rates[code] = Decimal(str(value))
    if rates.get("USD") != 1 or len(rates) < MIN_CURRENCIES:
        raise RatesError("too few rates")
    return {"rates": rates, "updated": updated}


def fetch_rates(opener=urllib.request.urlopen):
    """Güncel kurları indirir. opener testlerde sahte bir fonksiyonla değiştirilir."""
    request = urllib.request.Request(API_URL, headers={"User-Agent": f"UnitConverter/{VERSION}"})
    with opener(request, timeout=TIMEOUT_SECONDS) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise RatesError("response too large")
    try:
        data = json.loads(body)
    except ValueError:
        raise RatesError("invalid JSON") from None
    return parse_rates(data)


def to_cache(result, fetched_at):
    """Kayıt biçimi API yanıtıyla aynıdır; böylece okurken aynı doğrulamadan geçer."""
    return {
        "result": "success",
        "base_code": "USD",
        "time_last_update_unix": result["updated"],
        "fetched_at": int(fetched_at),
        "rates": {code: float(value) for code, value in result["rates"].items()},
    }


def load_cached():
    """Kayıtlı kurlar; dosya yoksa ya da bozuksa None."""
    data = load_json(CACHE_FILE, None)
    try:
        result = parse_rates(data)
    except RatesError:
        return None
    fetched_at = data.get("fetched_at")
    result["fetched_at"] = fetched_at if isinstance(fetched_at, int) and not isinstance(fetched_at, bool) else 0
    return result


def get_rates(now=None, fetch=fetch_rates):
    """Kurları ve durumunu döndürür: (sonuç, durum).

    Durumlar: "cached" (kayıt yeterince yeni), "fresh" (yeni indirildi),
    "offline" (indirilemedi, eski kayıt kullanılıyor), "unavailable" (ikisi de yok).
    """
    now = time.time() if now is None else now
    cached = load_cached()
    if cached and 0 <= now - cached["fetched_at"] < REFRESH_AFTER_SECONDS:
        return cached, "cached"
    try:
        result = fetch()
    except (OSError, http.client.HTTPException, RatesError):  # bağlantı kopması, zaman aşımı, yarım yanıt
        return (cached, "offline") if cached else (None, "unavailable")
    result["fetched_at"] = int(now)
    save_json(CACHE_FILE, to_cache(result, now))
    return result, "fresh"