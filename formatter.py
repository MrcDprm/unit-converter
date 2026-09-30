"""Sonuçları okunur biçimde yazar: dile göre ondalık ve binlik ayırıcı, çok büyük ve çok küçük
sayılar için bilimsel gösterim. Yazılan metin parse_number ile geri okunabilir."""
from decimal import ROUND_HALF_EVEN, Decimal

SIGNIFICANT_DIGITS = 12
SCIENTIFIC_ABOVE = Decimal("1e15")
SCIENTIFIC_BELOW = Decimal("1e-6")
SEPARATORS = {"tr": (",", "."), "en": (".", ",")}  # (ondalık, binlik)


def round_significant(value, digits=SIGNIFICANT_DIGITS):
    """Sayıyı anlamlı basamağa yuvarlar: 0.30000000000000004 → 0.3, 123456.789 → 123456.789."""
    if value == 0:
        return Decimal(0)
    exponent = value.adjusted() - digits + 1
    return value.quantize(Decimal(1).scaleb(exponent), rounding=ROUND_HALF_EVEN)


def format_number(value, lang="tr", grouping=True):
    rounded = round_significant(value)
    if rounded == 0:
        return "0"  # -0 de 0 olarak yazılır
    decimal_sep, group_sep = SEPARATORS[lang]

    magnitude = abs(rounded)
    if magnitude >= SCIENTIFIC_ABOVE or magnitude < SCIENTIFIC_BELOW:
        mantissa, exponent = f"{rounded:.{SIGNIFICANT_DIGITS - 1}E}".split("E")
        mantissa = mantissa.rstrip("0").rstrip(".")
        return f"{mantissa.replace('.', decimal_sep)}E{int(exponent):+d}"

    text = f"{rounded:,f}" if grouping else f"{rounded:f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    # Önce geçici bir işaret: virgül ve nokta yer değiştirirken birbirine karışmasın
    return text.replace(",", "\0").replace(".", decimal_sep).replace("\0", group_sep)