"""Arayüz metinleri (Türkçe / İngilizce). {name} yer tutucuları çağrılırken doldurulur."""
import time

MESSAGES = {
    "tr": {
        "app_name": "Birim Dönüştürücü",
        "from": "Dönüştürülecek",
        "to": "Sonuç",
        "swap": "Birimleri değiştir (Ctrl+R)",
        "copy": "Sonucu kopyala",
        "copied": "Kopyalandı: {value}",
        "all_units": "Tüm birimler",
        "unit": "Birim",
        "value": "Değer",
        "history": "Geçmiş",
        "clear_history": "Geçmişi temizle",
        "history_empty": "Henüz dönüşüm yok",
        "theme": "Temayı değiştir",
        "language": "English",
        "about": "Hakkında",
        "version": "Sürüm {version}",
        "about_text": "Python ve Tkinter ile yazılmış birim dönüştürücü. Döviz kurları ExchangeRate-API'den alınır.",
        "view_on_github": "GitHub'da görüntüle",
        "refresh": "Kurları yenile",
        "rates_loading": "Döviz kurları yükleniyor…",
        "rates_ok": "Kurlar: {date} · Kaynak: ",
        "rates_offline": "İnternet bağlantısı yok; {date} tarihli kurlar kullanılıyor · Kaynak: ",
        "rates_unavailable": "Döviz kurları alınamadı. İnternet bağlantını kontrol edip kurları yenile.",
        "rates_note": "Günlük referans kurlardır, anlık piyasa değildir.",
        "error_empty": "",
        "error_invalid": "Geçerli bir sayı yaz (ör. 12,5).",
        "error_too_long": "Sayı çok uzun.",
        "error_out_of_range": "Sayı çok büyük ya da çok küçük.",
        "error_below_absolute_zero": "Mutlak sıfırın (−273,15 °C) altında sıcaklık olamaz.",
        "error_no_rates": "Döviz kurları henüz yok.",
        "error_unknown_unit": "Bilinmeyen birim.",
        "unexpected_error": "Beklenmeyen bir hata oluştu. Uygulama çalışmaya devam ediyor.",
    },
    "en": {
        "app_name": "Unit Converter",
        "from": "Convert",
        "to": "Result",
        "swap": "Swap units (Ctrl+R)",
        "copy": "Copy result",
        "copied": "Copied: {value}",
        "all_units": "All units",
        "unit": "Unit",
        "value": "Value",
        "history": "History",
        "clear_history": "Clear history",
        "history_empty": "No conversions yet",
        "theme": "Toggle theme",
        "language": "Türkçe",
        "about": "About",
        "version": "Version {version}",
        "about_text": "A unit converter written in Python and Tkinter. Exchange rates come from ExchangeRate-API.",
        "view_on_github": "View on GitHub",
        "refresh": "Refresh rates",
        "rates_loading": "Loading exchange rates…",
        "rates_ok": "Rates: {date} · Source: ",
        "rates_offline": "No internet connection; using rates from {date} · Source: ",
        "rates_unavailable": "Could not load exchange rates. Check your connection and refresh the rates.",
        "rates_note": "Daily reference rates, not live market prices.",
        "error_empty": "",
        "error_invalid": "Enter a valid number (e.g. 12.5).",
        "error_too_long": "The number is too long.",
        "error_out_of_range": "The number is too large or too small.",
        "error_below_absolute_zero": "Temperature cannot be below absolute zero (−273.15 °C).",
        "error_no_rates": "Exchange rates are not available yet.",
        "error_unknown_unit": "Unknown unit.",
        "unexpected_error": "An unexpected error occurred. The app keeps running.",
    },
}

# Listede önce gösterilen yaygın para birimleri; diğerleri alfabetik sırayla gelir
COMMON_CURRENCIES = ["TRY", "USD", "EUR", "GBP", "CHF", "JPY", "CNY", "RUB", "SAR", "AED", "AZN", "CAD", "AUD"]

CURRENCY_NAMES = {
    "tr": {
        "TRY": "Türk lirası", "USD": "ABD doları", "EUR": "Euro", "GBP": "İngiliz sterlini",
        "CHF": "İsviçre frangı", "JPY": "Japon yeni", "CNY": "Çin yuanı", "RUB": "Rus rublesi",
        "SAR": "Suudi riyali", "AED": "BAE dirhemi", "AZN": "Azerbaycan manatı", "CAD": "Kanada doları",
        "AUD": "Avustralya doları", "SEK": "İsveç kronu", "NOK": "Norveç kronu", "DKK": "Danimarka kronu",
        "KWD": "Kuveyt dinarı", "QAR": "Katar riyali", "INR": "Hindistan rupisi", "BRL": "Brezilya reali",
        "KRW": "Güney Kore wonu", "MXN": "Meksika pesosu", "PLN": "Polonya zlotisi", "BGN": "Bulgar levası",
        "RON": "Rumen leyi", "GEL": "Gürcü larisi", "UAH": "Ukrayna grivnası", "EGP": "Mısır lirası",
    },
    "en": {
        "TRY": "Turkish lira", "USD": "US dollar", "EUR": "Euro", "GBP": "British pound",
        "CHF": "Swiss franc", "JPY": "Japanese yen", "CNY": "Chinese yuan", "RUB": "Russian ruble",
        "SAR": "Saudi riyal", "AED": "UAE dirham", "AZN": "Azerbaijani manat", "CAD": "Canadian dollar",
        "AUD": "Australian dollar", "SEK": "Swedish krona", "NOK": "Norwegian krone", "DKK": "Danish krone",
        "KWD": "Kuwaiti dinar", "QAR": "Qatari riyal", "INR": "Indian rupee", "BRL": "Brazilian real",
        "KRW": "South Korean won", "MXN": "Mexican peso", "PLN": "Polish złoty", "BGN": "Bulgarian lev",
        "RON": "Romanian leu", "GEL": "Georgian lari", "UAH": "Ukrainian hryvnia", "EGP": "Egyptian pound",
    },
}

MONTHS = {
    "tr": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
}


def translate(lang, key, **params):
    text = MESSAGES.get(lang, MESSAGES["en"]).get(key) or MESSAGES["en"].get(key, key)
    return text.format(**params) if params else text


def format_date(timestamp, lang):
    """Unix zamanını "30 Eylül 2026" / "September 30, 2026" biçiminde yazar (yerel saat)."""
    moment = time.localtime(timestamp)
    month = MONTHS[lang][moment.tm_mon - 1]
    return f"{moment.tm_mday} {month} {moment.tm_year}" if lang == "tr" else f"{month} {moment.tm_mday}, {moment.tm_year}"


def currency_label(code, lang):
    name = CURRENCY_NAMES[lang].get(code)
    return f"{code} – {name}" if name else code


def sort_currencies(codes):
    common = [code for code in COMMON_CURRENCIES if code in codes]
    return common + sorted(code for code in codes if code not in COMMON_CURRENCIES)
