"""Kullanıcı ayarları: dil, tema, seçili kategori ve her kategoride son seçilen birimler.

Dosyadan okunan değerlere güvenilmez; bilinmeyen ya da bozuk değer yerine varsayılan kullanılır.
"""
import re

from storage import load_json, save_json
from units import CATEGORIES

SETTINGS_FILE = "settings.json"
LANGUAGES = ("tr", "en")
THEMES = ("dark", "light")
UNIT_KEY = re.compile(r"[A-Za-z0-9_]{1,20}")


def default_settings(lang="tr"):
    return {"lang": lang, "theme": "dark", "category": "length", "units": {}}


def clean_settings(data, fallback_lang="tr"):
    settings = default_settings(fallback_lang)
    if not isinstance(data, dict):
        return settings
    if data.get("lang") in LANGUAGES:
        settings["lang"] = data["lang"]
    if data.get("theme") in THEMES:
        settings["theme"] = data["theme"]
    if data.get("category") in CATEGORIES:
        settings["category"] = data["category"]
    units = data.get("units")
    if isinstance(units, dict):
        for category, pair in units.items():
            if (
                category in CATEGORIES
                and isinstance(pair, list)
                and len(pair) == 2
                and all(isinstance(key, str) and UNIT_KEY.fullmatch(key) for key in pair)
            ):
                settings["units"][category] = list(pair)
    return settings


def load_settings(fallback_lang="tr"):
    return clean_settings(load_json(SETTINGS_FILE, None), fallback_lang)


def save_settings(settings):
    save_json(SETTINGS_FILE, settings)
