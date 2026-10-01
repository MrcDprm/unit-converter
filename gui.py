"""Arayüz: kategoriler, iki yönlü dönüşüm, tüm birimler tablosu, geçmiş ve döviz durumu.

Hesaplar converter.py'de, kurlar currency.py'de, kayıtlar history.py ve settings.py'dedir;
bu dosya sadece ekranı kurar ve olayları bu modüllere bağlar.
"""
import queue
import sys
import threading
import tkinter as tk
import traceback
import webbrowser
from decimal import Decimal
from tkinter import messagebox, ttk

from app_info import REPOSITORY_URL, VERSION, resource_path
from converter import ConversionError, convert, convert_all, parse_number, unit_keys
from currency import get_rates
from formatter import format_number
from history import add_entry, load_history, make_entry, save_history
from i18n import currency_label, format_date, sort_currencies, translate
from settings import load_settings, save_settings
from units import CATEGORIES, find_unit

RATES_SOURCE_URL = "https://www.exchangerate-api.com"
HISTORY_DELAY_MS = 1500
ALLOWED_INPUT = set("0123456789.,-+eE ")
MAX_INPUT = 40
FONT = "Segoe UI"

THEMES = {
    "dark": {
        "background": "#202020", "panel": "#2b2b2b", "field": "#1c1c1c", "text": "#ffffff",
        "muted": "#9d9d9d", "accent": "#4cc2ff", "accent_text": "#000000", "hover": "#383838",
        "error": "#ff99a4", "line": "#3d3d3d",
    },
    "light": {
        "background": "#f3f3f3", "panel": "#ffffff", "field": "#fbfbfb", "text": "#1a1a1a",
        "muted": "#5f5f5f", "accent": "#005fb8", "accent_text": "#ffffff", "hover": "#e5e5e5",
        "error": "#c42b1c", "line": "#d4d4d4",
    },
}


class ConverterApp:
    def __init__(self, root):
        self.root = root
        root.report_callback_exception = self.on_unexpected_error
        self.set_icon()

        self.settings = load_settings()
        self.colors = THEMES[self.settings["theme"]]
        self.history = load_history()
        self.rates = None
        self.rates_updated = None
        self.rates_status = "loading"
        self.rates_queue = queue.Queue()
        self.rates_thread = None
        self.from_key = self.to_key = None
        self.source = "from"  # kullanıcının son yazdığı kutu
        self.updating = False  # kod kutuya yazarken "kullanıcı yazdı" sanılmasın
        self.last_conversion = None
        self.user_changed = False  # sadece kullanıcının yaptığı dönüşümler geçmişe yazılır
        self.history_timer = None

        self.style = ttk.Style(root)
        self.style.theme_use("clam")
        self.build_sidebar()
        self.build_main()
        self.build_history()
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)
        self.bind_keys()

        self.apply_theme()
        self.select_category(self.settings["category"])
        self.render_texts()
        self.fit_window()
        self.load_rates()
        self.from_entry.focus_set()
    

    # ---------- Kurulum ----------
    def build_sidebar(self):
        self.sidebar = tk.Frame(self.root, padx=10, pady=14)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.title_label = tk.Label(self.sidebar, font=(FONT, 13, "bold"), anchor="w")
        self.title_label.pack(fill="x", padx=6, pady=(0, 12))

        self.category_buttons = {}
        for category in CATEGORIES:
            button = tk.Button(
                self.sidebar, anchor="w", font=(FONT, 11), relief="flat", bd=0, padx=12, pady=7,
                cursor="hand2", command=lambda category=category: self.select_category(category),
            )
            button.pack(fill="x", pady=1)
            self.category_buttons[category] = button

        self.footer = tk.Frame(self.sidebar)
        self.footer.pack(side="bottom", fill="x")
        self.theme_button = self.small_button(self.footer, self.toggle_theme)
        self.language_button = self.small_button(self.footer, self.toggle_language)
        self.about_button = self.small_button(self.footer, self.show_about)

    def small_button(self, parent, command):
        button = tk.Button(parent, anchor="w", font=(FONT, 10), relief="flat", bd=0, padx=12, pady=5,
                           cursor="hand2", command=command)
        button.pack(fill="x", pady=1)
        return button

    def build_main(self):
        self.main = tk.Frame(self.root, padx=24, pady=18)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)

        self.category_title = tk.Label(self.main, font=(FONT, 20, "bold"), anchor="w")
        self.category_title.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        validate = (self.root.register(self.is_allowed_input), "%P")
        self.from_var, self.to_var = tk.StringVar(), tk.StringVar()
        self.from_label = tk.Label(self.main, font=(FONT, 10), anchor="w")
        self.from_label.grid(row=1, column=0, sticky="ew")
        self.from_entry = tk.Entry(self.main, textvariable=self.from_var, font=(FONT, 22), relief="flat", bd=8, width=1,
                                   validate="key", validatecommand=validate)
        self.from_entry.grid(row=2, column=0, sticky="ew")
        self.from_combo = ttk.Combobox(self.main, state="readonly", font=(FONT, 11), width=22)
        self.from_combo.grid(row=2, column=1, sticky="ew", padx=(10, 0))

        self.swap_button = tk.Button(self.main, text="⇅", font=(FONT, 14), relief="flat", bd=0, width=3,
                                     cursor="hand2", command=self.swap_units)
        self.swap_button.grid(row=3, column=0, sticky="w", pady=6)

        self.to_label = tk.Label(self.main, font=(FONT, 10), anchor="w")
        self.to_label.grid(row=4, column=0, sticky="ew")
        self.to_entry = tk.Entry(self.main, textvariable=self.to_var, font=(FONT, 22), relief="flat", bd=8, width=1,
                                 validate="key", validatecommand=validate)
        self.to_entry.grid(row=5, column=0, sticky="ew")
        self.to_combo = ttk.Combobox(self.main, state="readonly", font=(FONT, 11), width=22)
        self.to_combo.grid(row=5, column=1, sticky="ew", padx=(10, 0))

        status_row = tk.Frame(self.main)
        status_row.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        status_row.grid_columnconfigure(0, weight=1)
        self.status_row = status_row
        self.status_label = tk.Label(status_row, font=(FONT, 10), anchor="w", justify="left")
        self.status_label.grid(row=0, column=0, sticky="ew")
        self.copy_button = tk.Button(status_row, font=(FONT, 10, "bold"), relief="flat", bd=0, padx=14, pady=5,
                                     cursor="hand2", command=self.copy_result)
        self.copy_button.grid(row=0, column=1, sticky="e")

        # Döviz kategorisinde görünen kur satırı (kaynak linki kaynak gösterme şartıdır)
        self.rates_row = tk.Frame(self.main)
        self.rates_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.rates_label = tk.Label(self.rates_row, font=(FONT, 9), anchor="w")
        self.rates_label.pack(side="left")
        self.rates_link = tk.Label(self.rates_row, text="ExchangeRate-API", font=(FONT, 9, "underline"), cursor="hand2")
        self.rates_link.pack(side="left")
        self.rates_link.bind("<Button-1>", lambda event: webbrowser.open(RATES_SOURCE_URL))
        self.refresh_button = tk.Button(self.rates_row, font=(FONT, 9), relief="flat", bd=0, padx=10, pady=2,
                                        cursor="hand2", command=self.load_rates)
        self.refresh_button.pack(side="right")
        self.rates_note = tk.Label(self.main, font=(FONT, 9), anchor="w")
        self.rates_note.grid(row=8, column=0, columnspan=2, sticky="ew")

        self.table_label = tk.Label(self.main, font=(FONT, 11, "bold"), anchor="w")
        self.table_label.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(16, 4))
        self.table = ttk.Treeview(self.main, columns=("unit", "value"), show="headings", selectmode="browse")
        self.table.column("unit", width=260, anchor="w")
        self.table.column("value", width=260, anchor="e")
        self.table.grid(row=10, column=0, columnspan=2, sticky="nsew")
        self.main.grid_rowconfigure(10, weight=1)
        self.table.bind("<<TreeviewSelect>>", self.on_table_select)

        self.from_var.trace_add("write", lambda *args: self.on_input("from"))
        self.to_var.trace_add("write", lambda *args: self.on_input("to"))
        self.from_combo.bind("<<ComboboxSelected>>", lambda event: self.on_unit_selected())
        self.to_combo.bind("<<ComboboxSelected>>", lambda event: self.on_unit_selected())

    def build_history(self):
        self.history_frame = tk.Frame(self.root, padx=12, pady=18)
        self.history_frame.grid(row=0, column=2, sticky="ns")
        self.history_frame.grid_rowconfigure(1, weight=1)
        self.history_label = tk.Label(self.history_frame, font=(FONT, 11, "bold"), anchor="w")
        self.history_label.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.history_list = tk.Listbox(self.history_frame, font=(FONT, 10), width=28, relief="flat", bd=0,
                                       highlightthickness=0, activestyle="none")
        self.history_list.grid(row=1, column=0, sticky="nsew")
        self.history_list.bind("<<ListboxSelect>>", self.on_history_select)
        self.clear_button = tk.Button(self.history_frame, font=(FONT, 10), relief="flat", bd=0, pady=5,
                                      cursor="hand2", command=self.clear_history)
        self.clear_button.grid(row=2, column=0, sticky="ew", pady=(8, 0))

    def bind_keys(self):
        for index, category in enumerate(CATEGORIES, start=1):
            self.root.bind(f"<Control-Key-{index}>", lambda event, category=category: self.select_category(category))
        self.root.bind("<Control-r>", lambda event: self.swap_units())
        self.root.bind("<Control-Shift-C>", lambda event: self.copy_result())
        self.root.bind("<F5>", lambda event: self.load_rates())
        self.root.bind("<Return>", lambda event: self.commit_history())
        self.root.bind("<Escape>", lambda event: self.clear_input())

    def fit_window(self):
        """Pencere boyutu ekran ölçeğine göre ayarlanır: %150 ölçekte yazılar büyür, pencere de büyümeli."""
        self.root.update_idletasks()
        scale = self.root.winfo_fpixels("1i") / 96
        needed_width, needed_height = self.root.winfo_reqwidth(), self.root.winfo_reqheight()
        width = min(max(int(1180 * scale), needed_width), self.root.winfo_screenwidth() - 40)
        height = min(max(int(700 * scale), needed_height), self.root.winfo_screenheight() - 80)
        left = (self.root.winfo_screenwidth() - width) // 2
        top = max(0, (self.root.winfo_screenheight() - height) // 2 - 20)  # görev çubuğu için biraz yukarı
        self.root.geometry(f"{width}x{height}+{left}+{top}")
        self.root.minsize(min(needed_width, width), min(needed_height, height))

    def set_icon(self):
        try:
            self.root.iconbitmap(default=resource_path("assets/icon.ico"))
        except tk.TclError:
            pass

    # ---------- Metinler ve tema ----------

    def t(self, key, **params):
        return translate(self.settings["lang"], key, **params)

    def render_texts(self):
        lang = self.settings["lang"]
        self.root.title(self.t("app_name"))
        self.title_label.config(text=self.t("app_name"))
        for category, button in self.category_buttons.items():
            button.config(text=CATEGORIES[category]["name"][lang])
        self.category_title.config(text=CATEGORIES[self.settings["category"]]["name"][lang])
        self.theme_button.config(text=("☀  " if self.settings["theme"] == "dark" else "☾  ") + self.t("theme"))
        self.language_button.config(text="🌐  " + self.t("language"))
        self.about_button.config(text="ⓘ  " + self.t("about"))
        self.from_label.config(text=self.t("from"))
        self.to_label.config(text=self.t("to"))
        self.copy_button.config(text=self.t("copy"))
        self.refresh_button.config(text="⟳ " + self.t("refresh"))
        self.rates_note.config(text=self.t("rates_note"))
        self.table_label.config(text=self.t("all_units"))
        self.table.heading("unit", text=self.t("unit"))
        self.table.heading("value", text=self.t("value"))
        self.history_label.config(text=self.t("history"))
        self.clear_button.config(text=self.t("clear_history"))
        self.render_units()
        self.render_rates_row()
        self.render_history()
        self.recalculate()

    def apply_theme(self):
        c = self.colors
        for frame in (self.root, self.sidebar, self.footer, self.main, self.status_row, self.rates_row,
                      self.history_frame):
            frame.config(bg=c["background"])
        for label in (self.title_label, self.category_title, self.table_label, self.history_label):
            label.config(bg=c["background"], fg=c["text"])
        for label in (self.from_label, self.to_label, self.rates_label, self.rates_note):
            label.config(bg=c["background"], fg=c["muted"])
        self.rates_link.config(bg=c["background"], fg=c["accent"])
        self.status_label.config(bg=c["background"])
        for entry in (self.from_entry, self.to_entry):
            entry.config(bg=c["field"], fg=c["text"], insertbackground=c["text"], highlightthickness=1,
                         highlightbackground=c["line"], highlightcolor=c["accent"])
        for button in (self.swap_button, self.refresh_button, self.clear_button):
            button.config(bg=c["panel"], fg=c["text"], activebackground=c["hover"], activeforeground=c["text"])
        for button in (self.theme_button, self.language_button, self.about_button):
            button.config(bg=c["background"], fg=c["text"], activebackground=c["hover"], activeforeground=c["text"])
        self.copy_button.config(bg=c["accent"], fg=c["accent_text"], activebackground=c["accent"],
                                activeforeground=c["accent_text"])
        self.history_list.config(bg=c["background"], fg=c["text"], selectbackground=c["hover"],
                                 selectforeground=c["text"])
        self.paint_categories()

        self.style.configure("TCombobox", fieldbackground=c["field"], background=c["panel"], foreground=c["text"],
                             arrowcolor=c["text"], bordercolor=c["line"], lightcolor=c["field"], darkcolor=c["field"])
        self.style.map("TCombobox", fieldbackground=[("readonly", c["field"])], foreground=[("readonly", c["text"])],
                       selectbackground=[("readonly", c["field"])], selectforeground=[("readonly", c["text"])])
        self.style.configure("Treeview", background=c["field"], fieldbackground=c["field"], foreground=c["text"],
                             bordercolor=c["line"], lightcolor=c["line"], darkcolor=c["line"], rowheight=26,
                             font=(FONT, 10))
        self.style.map("Treeview", background=[("selected", c["hover"])], foreground=[("selected", c["text"])])
        self.style.configure("Treeview.Heading", background=c["panel"], foreground=c["muted"], relief="flat",
                             font=(FONT, 9, "bold"))
        self.style.map("Treeview.Heading", background=[("active", c["hover"])])
        # Açılır listenin renkleri: yeni oluşturulan listeler için seçenek, var olanlar için doğrudan ayar
        self.root.option_add("*TCombobox*Listbox.background", c["panel"])
        self.root.option_add("*TCombobox*Listbox.foreground", c["text"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", c["accent"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", c["accent_text"])
        for combo in (self.from_combo, self.to_combo):
            try:
                popdown = combo.tk.eval(f"ttk::combobox::PopdownWindow {combo}")
                combo.tk.call(f"{popdown}.f.l", "configure", "-background", c["panel"], "-foreground", c["text"],
                              "-selectbackground", c["accent"], "-selectforeground", c["accent_text"])
            except tk.TclError:
                pass

    def paint_categories(self):
        c = self.colors
        for category, button in self.category_buttons.items():
            selected = category == self.settings["category"]
            button.config(bg=c["panel"] if selected else c["background"], fg=c["accent"] if selected else c["text"],
                          activebackground=c["hover"], activeforeground=c["text"])

    def toggle_theme(self):
        self.settings["theme"] = "light" if self.settings["theme"] == "dark" else "dark"
        self.colors = THEMES[self.settings["theme"]]
        save_settings(self.settings)
        self.apply_theme()
        self.render_texts()

    def toggle_language(self):
        old = self.settings["lang"]
        new = "en" if old == "tr" else "tr"
        # Kutudaki sayı yeni dilin ayırıcılarıyla yeniden yazılır ("12,5" → "12.5")
        source_var = self.from_var if self.source == "from" else self.to_var
        try:
            value = parse_number(source_var.get(), old)
        except ConversionError:
            value = None
        self.settings["lang"] = new
        save_settings(self.settings)
        if value is not None:
            self.set_text(source_var, format_number(value, new))
        self.render_texts()

    # ---------- Kategori ve birimler ----------

    def keys(self):
        return unit_keys(self.settings["category"], self.rates)

    def unit_label(self, key):
        category = self.settings["category"]
        lang = self.settings["lang"]
        if CATEGORIES[category]["kind"] == "currency":
            return currency_label(key, lang)
        unit = find_unit(category, key)
        return f"{unit['name'][lang]} ({unit['symbol']})"

    def unit_symbol(self, category, key):
        if CATEGORIES[category]["kind"] == "currency":
            return key
        unit = find_unit(category, key)
        return unit["symbol"] if unit else key

    def ordered_keys(self):
        keys = self.keys()
        return sort_currencies(keys) if CATEGORIES[self.settings["category"]]["kind"] == "currency" else keys

    def pick_units(self, category):
        """Kategoride en son seçilen birim çifti; artık geçerli değilse varsayılan çift."""
        keys = unit_keys(category, self.rates)
        saved = self.settings["units"].get(category)
        return saved if saved and all(key in keys for key in saved) else CATEGORIES[category]["default"]

    def select_category(self, category):
        self.commit_history()
        self.settings["category"] = category
        self.from_key, self.to_key = self.pick_units(category)
        self.set_text(self.from_var, "1")  # önceki kategorinin değeri yeni kategoride anlamsız olabilir
        self.source = "from"
        save_settings(self.settings)
        self.paint_categories()
        self.category_title.config(text=CATEGORIES[category]["name"][self.settings["lang"]])
        self.render_units()
        self.render_rates_row()
        self.recalculate()

    def render_units(self):
        keys = self.ordered_keys()
        labels = [self.unit_label(key) for key in keys]
        self.unit_order = keys
        for combo, key in ((self.from_combo, self.from_key), (self.to_combo, self.to_key)):
            combo.config(values=labels)
            if key in keys:
                combo.current(keys.index(key))
            else:
                combo.set("")

    def on_unit_selected(self):
        if self.from_combo.current() >= 0:
            self.from_key = self.unit_order[self.from_combo.current()]
        if self.to_combo.current() >= 0:
            self.to_key = self.unit_order[self.to_combo.current()]
        self.remember_units()
        self.recalculate()
        self.schedule_history()
        self.from_entry.focus_set()

    def swap_units(self):
        self.from_key, self.to_key = self.to_key, self.from_key
        self.source = "from"
        self.remember_units()
        self.render_units()
        self.recalculate()
        self.schedule_history()

    def remember_units(self):
        if self.from_key and self.to_key:
            self.settings["units"][self.settings["category"]] = [self.from_key, self.to_key]
            save_settings(self.settings)

    # ---------- Dönüşüm ----------

    def is_allowed_input(self, text):
        return len(text) <= MAX_INPUT and all(char in ALLOWED_INPUT for char in text)

    def set_text(self, variable, text):
        self.updating = True
        try:
            variable.set(text)
        finally:
            self.updating = False

    def on_input(self, side):
        if self.updating:
            return
        self.source = side
        self.recalculate()
        self.schedule_history()

    def recalculate(self):
        category = self.settings["category"]
        lang = self.settings["lang"]
        if self.source == "from":
            source_var, target_var, from_key, to_key = self.from_var, self.to_var, self.from_key, self.to_key
        else:
            source_var, target_var, from_key, to_key = self.to_var, self.from_var, self.to_key, self.from_key
        try:
            value = parse_number(source_var.get(), lang)
            if from_key is None or to_key is None:
                raise ConversionError("no_rates")
            result = convert(category, value, from_key, to_key, self.rates)
        except ConversionError as error:
            self.set_text(target_var, "")
            self.show_status(self.t(f"error_{error.code}"), error=True)
            self.fill_table(None, None)
            self.last_conversion = None
            return
        self.set_text(target_var, format_number(result, lang))
        self.show_status("")
        self.fill_table(value, from_key)
        self.last_conversion = make_entry(category, value, from_key, to_key, result)

    def fill_table(self, value, from_key):
        self.table.delete(*self.table.get_children())
        if value is None:
            return
        category = self.settings["category"]
        lang = self.settings["lang"]
        results = dict(convert_all(category, value, from_key, self.rates))
        for key in self.ordered_keys():
            if key in results:
                self.table.insert("", "end", iid=key, values=(self.unit_label(key), format_number(results[key], lang)))

    def show_status(self, text, error=False):
        self.status_label.config(text=text, fg=self.colors["error"] if error else self.colors["muted"])

    def copy_result(self):
        text = (self.to_var if self.source == "from" else self.from_var).get()
        if text:
            self.copy(text)
            self.user_changed = True
            self.commit_history()

    def copy(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.show_status(self.t("copied", value=text))

    def on_table_select(self, event):
        selection = self.table.selection()
        if selection:
            self.copy(self.table.item(selection[0], "values")[1])

    def clear_input(self):
        self.source = "from"
        self.set_text(self.from_var, "")
        self.recalculate()
        self.from_entry.focus_set()

    # ---------- Geçmiş ----------

    def schedule_history(self):
        self.user_changed = True
        if self.history_timer:
            self.root.after_cancel(self.history_timer)
        self.history_timer = self.root.after(HISTORY_DELAY_MS, self.commit_history)

    def commit_history(self):
        if self.history_timer:
            self.root.after_cancel(self.history_timer)
            self.history_timer = None
        if self.last_conversion is None or not self.user_changed:
            return
        self.user_changed = False
        if self.history and self.history[0] == self.last_conversion:
            return
        self.history = add_entry(self.history, self.last_conversion)
        save_history(self.history)
        self.render_history()

    def render_history(self):
        lang = self.settings["lang"]
        self.history_list.delete(0, "end")
        if not self.history:
            self.history_list.insert("end", self.t("history_empty"))
            self.history_list.itemconfig(0, fg=self.colors["muted"])
            return
        for entry in self.history:
            category = entry["category"]
            value = format_number(Decimal(entry["value"]), lang)
            result = format_number(Decimal(entry["result"]), lang)
            self.history_list.insert(
                "end",
                f"{value} {self.unit_symbol(category, entry['from'])} = {result} {self.unit_symbol(category, entry['to'])}",
            )

    def on_history_select(self, event):
        selection = self.history_list.curselection()
        if not selection or not self.history:
            return
        entry = self.history[selection[0]]
        self.history_list.selection_clear(0, "end")
        self.select_category(entry["category"])
        keys = self.keys()
        if entry["from"] in keys and entry["to"] in keys:
            self.from_key, self.to_key = entry["from"], entry["to"]
            self.remember_units()
            self.render_units()
        self.source = "from"
        self.set_text(self.from_var, format_number(Decimal(entry["value"]), self.settings["lang"]))
        self.recalculate()

    def clear_history(self):
        self.history = []
        save_history(self.history)
        self.render_history()

    # ---------- Döviz kurları ----------

    def load_rates(self):
        """Kurlar ayrı bir iş parçacığında indirilir; pencere donmaz. Sonuç kuyruktan okunur."""
        if self.rates_thread and self.rates_thread.is_alive():
            return  # önceki indirme sürüyor; F5'e üst üste basmak yeni istek açmasın
        self.rates_status = "loading"
        self.render_rates_row()
        self.rates_thread = threading.Thread(target=lambda: self.rates_queue.put(get_rates()), daemon=True)
        self.rates_thread.start()
        self.root.after(100, self.poll_rates)

    def poll_rates(self):
        try:
            result, status = self.rates_queue.get_nowait()
        except queue.Empty:
            self.root.after(100, self.poll_rates)
            return
        self.rates_status = status
        if result:
            self.rates = result["rates"]
            self.rates_updated = result["updated"]
        self.render_rates_row()
        if CATEGORIES[self.settings["category"]]["kind"] == "currency":
            self.from_key, self.to_key = self.pick_units("currency")
            self.render_units()
            self.recalculate()

    def render_rates_row(self):
        is_currency = CATEGORIES[self.settings["category"]]["kind"] == "currency"
        if not is_currency:
            self.rates_row.grid_remove()
            self.rates_note.grid_remove()
            return
        self.rates_row.grid()
        self.rates_note.grid()
        lang = self.settings["lang"]
        show_link = self.rates_status in ("fresh", "cached", "offline")
        if self.rates_status == "loading":
            text = self.t("rates_loading")
        elif self.rates_status == "unavailable":
            text = self.t("rates_unavailable")
        else:
            key = "rates_offline" if self.rates_status == "offline" else "rates_ok"
            text = self.t(key, date=format_date(self.rates_updated, lang))
        self.rates_label.config(text=text, fg=self.colors["error"] if self.rates_status in ("offline", "unavailable") else self.colors["muted"])
        if show_link:
            self.rates_link.pack(side="left")
        else:
            self.rates_link.pack_forget()
        # Kurlar günde bir güncellenir; yenile düğmesi sadece indirme başarısızsa işe yarar
        if self.rates_status in ("offline", "unavailable"):
            self.refresh_button.pack(side="right")
        else:
            self.refresh_button.pack_forget()

    # ---------- Diğer ----------

    def show_about(self):
        c = self.colors
        window = tk.Toplevel(self.root, bg=c["background"], padx=28, pady=22)
        window.title(self.t("about"))
        window.resizable(False, False)
        window.transient(self.root)
        window.geometry(f"+{self.root.winfo_rootx() + 80}+{self.root.winfo_rooty() + 80}")
        for text, font in (
            (self.t("app_name"), (FONT, 16, "bold")),
            (self.t("version", version=VERSION), (FONT, 11)),
            (self.t("about_text"), (FONT, 10)),
            ("© 2026 Miraç Deprem", (FONT, 9)),
        ):
            tk.Label(window, text=text, font=font, wraplength=320, justify="center", bg=c["background"],
                     fg=c["text"]).pack(pady=2)
        link = tk.Label(window, text=self.t("view_on_github"), font=(FONT, 10, "underline"), cursor="hand2",
                        bg=c["background"], fg=c["accent"])
        link.pack(pady=(10, 0))
        link.bind("<Button-1>", lambda event: webbrowser.open(REPOSITORY_URL))
        window.bind("<Escape>", lambda event: window.destroy())
        window.grab_set()
        window.focus_set()

    def on_unexpected_error(self, exc_type, exc_value, exc_traceback):
        # Ayrıntı kullanıcıya değil konsola yazılır; kullanıcı sade bir mesaj görür ve uygulama çalışmaya devam eder
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
        messagebox.showerror(self.t("app_name"), self.t("unexpected_error"), parent=self.root)

