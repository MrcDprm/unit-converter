# Unit Converter

**English** | [Türkçe](README.tr.md)

A desktop unit converter written in Python and Tkinter: nine categories including live currency rates, Turkish kitchen measures and the difference between GB and GiB.

> 🚧 Work in progress. This README is the project plan and will be completed at v1.0.0.

## Plan

### MVP
- **Categories:** length, weight, temperature, volume, area, speed, time, data size and currency.
- **Real-world touches:**
  - Turkish kitchen measures in volume (su bardağı, çay bardağı, yemek kaşığı, tatlı kaşığı, çay kaşığı) next to US cups and fluid ounces.
  - Data size in both decimal (GB) and binary (GiB) units, which explains why a 1 TB disk shows up as 931 GB.
- **Currency:** 166 currencies from the free, keyless ExchangeRate-API. Rates are cached with their date, so the app keeps working offline with the last known rates and says how old they are.
- **Live, two-way conversion:** type in either box and the other updates; a swap button flips the units.
- **All units at a glance:** a table with the value in every unit of the category; clicking a row copies it.
- **History:** the last 50 conversions, reopened with a click and cleared with one button.
- **Accuracy:** calculations use `Decimal`, temperature below absolute zero is rejected, very large and small numbers use scientific notation, and a Turkish decimal comma (`3,5`) is accepted.
- **Usability:** copy button and Ctrl+C, remembered category and units, dark and light theme, keyboard shortcuts, Turkish and English.
- **Desktop app:** icon, version, About window, settings saved in the user's folder, Windows installer (PyInstaller + Inno Setup).
- **Tests:** every conversion, round trips (A → B → A), temperature edge cases, currency cache and history.

### Future Plans
- Favourite unit pairs.
- Pressure, energy and fuel economy (L/100 km ↔ mpg).
- Charts of past exchange rates.

## Tech Stack
- Python 3, Tkinter
- `decimal` for exact arithmetic
- [ExchangeRate-API](https://www.exchangerate-api.com) open access (free, no API key)
- `unittest`
- PyInstaller, Inno Setup
