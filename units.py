"""Kategoriler ve birimler.

Her doğrusal birimin katsayısı, kategorinin temel birimi cinsinden değeridir
(uzunlukta temel birim metre: 1 km = 1000 m). Katsayılar metin olarak yazılır ki
Decimal'e çevrilirken ikili kayan nokta yuvarlaması olmasın.
Sıcaklık katsayıyla değil formülle, döviz ise indirilen kurlarla çevrilir.
"""
from decimal import Decimal


def unit(key, symbol, name_tr, name_en, factor=None):
    return {
        "key": key,
        "symbol": symbol,
        "name": {"tr": name_tr, "en": name_en},
        "factor": Decimal(factor) if factor is not None else None,
    }


CATEGORIES = {
    "length": {
        "name": {"tr": "Uzunluk", "en": "Length"},
        "kind": "linear",
        "default": ("m", "ft"),
        "units": [
            unit("mm", "mm", "Milimetre", "Millimeter", "0.001"),
            unit("cm", "cm", "Santimetre", "Centimeter", "0.01"),
            unit("m", "m", "Metre", "Meter", "1"),
            unit("km", "km", "Kilometre", "Kilometer", "1000"),
            unit("in", "in", "İnç", "Inch", "0.0254"),
            unit("ft", "ft", "Fit", "Foot", "0.3048"),
            unit("yd", "yd", "Yarda", "Yard", "0.9144"),
            unit("mi", "mi", "Mil", "Mile", "1609.344"),
            unit("nmi", "nmi", "Deniz mili", "Nautical mile", "1852"),
        ],
    },
    "weight": {
        "name": {"tr": "Ağırlık", "en": "Weight"},
        "kind": "linear",
        "default": ("kg", "lb"),
        "units": [
            unit("mg", "mg", "Miligram", "Milligram", "0.000001"),
            unit("g", "g", "Gram", "Gram", "0.001"),
            unit("kg", "kg", "Kilogram", "Kilogram", "1"),
            unit("t", "t", "Ton", "Tonne", "1000"),
            unit("oz", "oz", "Ons", "Ounce", "0.028349523125"),
            unit("lb", "lb", "Libre", "Pound", "0.45359237"),
            unit("st", "st", "Stone", "Stone", "6.35029318"),
        ],
    },
    "temperature": {
        "name": {"tr": "Sıcaklık", "en": "Temperature"},
        "kind": "temperature",
        "default": ("c", "f"),
        "units": [
            unit("c", "°C", "Santigrat", "Celsius"),
            unit("f", "°F", "Fahrenhayt", "Fahrenheit"),
            unit("k", "K", "Kelvin", "Kelvin"),
        ],
    },
    "volume": {
        "name": {"tr": "Hacim", "en": "Volume"},
        "kind": "linear",
        "default": ("l", "su_bardagi"),
        "units": [
            unit("ml", "ml", "Mililitre", "Milliliter", "0.001"),
            unit("l", "L", "Litre", "Liter", "1"),
            unit("m3", "m³", "Metreküp", "Cubic meter", "1000"),
            # Türk mutfak ölçüleri: tariflerde kullanılan yaygın karşılıklar
            unit("su_bardagi", "su b.", "Su bardağı", "Turkish water glass", "0.2"),
            unit("cay_bardagi", "çay b.", "Çay bardağı", "Turkish tea glass", "0.1"),
            unit("yemek_kasigi", "y.k.", "Yemek kaşığı", "Tablespoon (TR)", "0.015"),
            unit("tatli_kasigi", "t.k.", "Tatlı kaşığı", "Dessert spoon (TR)", "0.01"),
            unit("cay_kasigi", "ç.k.", "Çay kaşığı", "Teaspoon (TR)", "0.005"),
            # ABD ölçüleri
            unit("cup", "cup", "Cup (ABD)", "Cup (US)", "0.2365882365"),
            unit("floz", "fl oz", "Sıvı ons (ABD)", "Fluid ounce (US)", "0.0295735295625"),
            unit("gal", "gal", "Galon (ABD)", "Gallon (US)", "3.785411784"),
        ],
    },
    "area": {
        "name": {"tr": "Alan", "en": "Area"},
        "kind": "linear",
        "default": ("m2", "donum"),
        "units": [
            unit("cm2", "cm²", "Santimetrekare", "Square centimeter", "0.0001"),
            unit("m2", "m²", "Metrekare", "Square meter", "1"),
            unit("donum", "dönüm", "Dönüm", "Dönüm", "1000"),
            unit("ha", "ha", "Hektar", "Hectare", "10000"),
            unit("km2", "km²", "Kilometrekare", "Square kilometer", "1000000"),
            unit("ft2", "ft²", "Fitkare", "Square foot", "0.09290304"),
            unit("acre", "ac", "Akre", "Acre", "4046.8564224"),
        ],
    },
    "speed": {
        # Temel birim km/sa: diğerleri ona göre sonlu ondalık sayılarla yazılabiliyor (m/s = 3,6 km/sa)
        "name": {"tr": "Hız", "en": "Speed"},
        "kind": "linear",
        "default": ("kmh", "mph"),
        "units": [
            unit("ms", "m/s", "Metre/saniye", "Meters per second", "3.6"),
            unit("kmh", "km/sa", "Kilometre/saat", "Kilometers per hour", "1"),
            unit("mph", "mph", "Mil/saat", "Miles per hour", "1.609344"),
            unit("kn", "kn", "Knot", "Knot", "1.852"),
        ],
    },
    "time": {
        "name": {"tr": "Zaman", "en": "Time"},
        "kind": "linear",
        "default": ("h", "min"),
        "units": [
            unit("ms_time", "ms", "Milisaniye", "Millisecond", "0.001"),
            unit("s", "sn", "Saniye", "Second", "1"),
            unit("min", "dk", "Dakika", "Minute", "60"),
            unit("h", "sa", "Saat", "Hour", "3600"),
            unit("day", "gün", "Gün", "Day", "86400"),
            unit("week", "hf", "Hafta", "Week", "604800"),
            # Ortalama Gregoryen yıl: 365,2425 gün
            unit("year", "yıl", "Yıl", "Year", "31556952"),
        ],
    },
    "data": {
        # Diskler 10'luk (1 GB = 10⁹ bayt), Windows 2'lik (1 GiB = 2³⁰ bayt) birim kullanır
        "name": {"tr": "Veri boyutu", "en": "Data size"},
        "kind": "linear",
        "default": ("tb", "gib"),
        "units": [
            unit("bit", "bit", "Bit", "Bit", "0.125"),
            unit("byte", "B", "Bayt", "Byte", "1"),
            unit("kb", "KB", "Kilobayt", "Kilobyte", "1000"),
            unit("mb", "MB", "Megabayt", "Megabyte", "1000000"),
            unit("gb", "GB", "Gigabayt", "Gigabyte", "1000000000"),
            unit("tb", "TB", "Terabayt", "Terabyte", "1000000000000"),
            unit("kib", "KiB", "Kibibayt", "Kibibyte", "1024"),
            unit("mib", "MiB", "Mebibayt", "Mebibyte", "1048576"),
            unit("gib", "GiB", "Gibibayt", "Gibibyte", "1073741824"),
            unit("tib", "TiB", "Tebibayt", "Tebibyte", "1099511627776"),
        ],
    },
    "currency": {
        # Birimler (para birimleri) indirilen kurlardan oluşturulur; bkz. currency.py
        "name": {"tr": "Döviz", "en": "Currency"},
        "kind": "currency",
        "default": ("USD", "TRY"),
        "units": [],
    },
}


def find_unit(category, key):
    """Kategorideki birimi anahtarıyla bulur; yoksa None."""
    for item in CATEGORIES[category]["units"]:
        if item["key"] == key:
            return item
    return None