# main_app.py
import os
import sys
import json
import threading
import queue
import time
import webbrowser
import customtkinter as ctk
from tkinter import messagebox
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageTk
import jh_ai_engine
import jh_storage_manager
import jh_results_ui

# =====================================================================
# НАСТРОЙКА DPI И СИСТЕМНОГО ОКРУЖЕНИЯ Windows
# =====================================================================
try:
    import ctypes
    # Включаем DPI-Awareness, чтобы шрифты на экранах (2K/4K) были идеально четкими
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Настройки путей к конфигурации
APPDATA_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'Job Hunter AI')
os.makedirs(APPDATA_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
LOGO_PNG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

# Инициализируем локальную БД
jh_storage_manager.init_db()

# Цветовая неоновая космическая палитра
COLOR_BG_DARK = "#090D14"       # Мягкий глубокий темный космос
COLOR_CARD_BG = "#111622"       # Спокойный сине-серый фон карточек
COLOR_INPUT_BG = "#171D2C"      # Пространство полей ввода / неактивных кнопок
COLOR_CYAN_NEON = "#00D8C6"     # Благородный мягкий циан (лого/успех)
COLOR_CYAN_HOVER = "#00A193"    # Глубокий бирюзовый (hover)
COLOR_GOLD = "#E2A33C"          # Теплое золото туманности (ожидание/актив)
COLOR_GOLD_HOVER = "#B3802F"    # Мягкий янтарный (hover)
COLOR_RED = "#D24B4B"           # Приглушенный красный (опасность/удаление)
COLOR_RED_HOVER = "#A83C3C"     # Глубокий вишневый (hover)
COLOR_TEXT_MUTED = "#828D9A"     # Пыльно-серый текст
COLOR_TEXT_LIGHT = "#E9EDF0"     # Комфортный белый звездный текст

# Доступные модели по провайдерам
ALL_PROVIDERS_MODELS = {
    "Gemini": ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.0-pro"],
    "OpenAI": ["gpt-5-mini", "gpt-5", "o3-mini"],
    "Anthropic": ["claude-4-haiku", "claude-4-sonnet", "claude-4-opus"],
    "DeepSeek": ["deepseek-chat", "deepseek-reasoner"]
}

# =====================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ИНТЕРФЕЙСА
# =====================================================================
def force_dark_title_bar(window):
    """Принудительно перекрашивает заголовок окна Windows в темный цвет"""
    try:
        import ctypes
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if hwnd == 0: hwnd = window.winfo_id()
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(ctypes.c_int(1)), 4)
    except Exception:
        pass

def center_window(window, width, height, parent=None):
    """Абсолютно стабильное центрирование без мерцания за счет альфа-канала."""
    try:
        window.attributes("-alpha", 0.0)
    except Exception:
        pass
    
    def _apply_centered_position():
        if not window.winfo_exists():
            return
        try:
            window.update_idletasks()
            try:
                scaling = window._get_window_scaling()
            except Exception:
                scaling = 1.0

            scaled_width = int(width * scaling)
            scaled_height = int(height * scaling)
            
            if parent and parent.winfo_exists():
                parent_x = parent.winfo_x()
                parent_y = parent.winfo_y()
                parent_w = parent.winfo_width()
                parent_h = parent.winfo_height()
                
                x = parent_x + (parent_w - scaled_width) // 2
                y = parent_y + (parent_h - scaled_height) // 2
            else:
                screen_width = window.winfo_screenwidth()
                screen_height = window.winfo_screenheight()
                
                x = (screen_width - scaled_width) // 2
                y = (screen_height - scaled_height) // 2
            
            x = max(0, int(x))
            y = max(0, int(y))
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            print(f"[Резервное центрирование]: {e}")
            window.geometry(f"{width}x{height}")
        finally:
            try:
                window.attributes("-alpha", 1.0)
                window.deiconify()
            except Exception:
                pass
        
    window.after(15, _apply_centered_position)

def bind_russian_hotkeys(widget):
    """Обработка горячих клавиш Ctrl+C, Ctrl+V, Ctrl+A, Ctrl+X для русской раскладки."""
    target = widget
    if hasattr(widget, "_entry"):
        target = widget._entry
    elif hasattr(widget, "_textbox"):
        target = widget._textbox

    def handle_control_keys(event):
        key = event.keysym.lower()
        keycode = event.keycode
        
        if keycode == 86 or key in ('v', 'cyrillic_em'):
            try:
                text = event.widget.clipboard_get()
                try:
                    if event.widget.tag_ranges("sel"):
                        event.widget.delete("sel.first", "sel.last")
                except Exception:
                    try:
                        if event.widget.selection_present():
                            event.widget.delete("sel.first", "sel.last")
                    except Exception:
                        pass
                event.widget.insert("insert", text)
            except Exception:
                pass
            return "break"
            
        elif keycode == 67 or key in ('c', 'cyrillic_es'):
            try:
                selected_text = None
                try:
                    selected_text = event.widget.get("sel.first", "sel.last")
                except Exception:
                    try:
                        selected_text = event.widget.selection_get()
                    except Exception:
                        pass
                if selected_text:
                    event.widget.clipboard_clear()
                    event.widget.clipboard_append(selected_text)
            except Exception:
                pass
            return "break"
            
        elif keycode == 65 or key in ('a', 'cyrillic_ef'):
            try:
                if hasattr(event.widget, "tag_add"):
                    event.widget.tag_add("sel", "1.0", "end-1c")
                    event.widget.mark_set("insert", "1.0")
                elif hasattr(event.widget, "select_range"):
                    event.widget.select_range(0, "end")
                    event.widget.icursor("end")
            except Exception:
                pass
            return "break"
            
        elif keycode == 88 or key in ('x', 'cyrillic_che'):
            try:
                selected_text = None
                try:
                    selected_text = event.widget.get("sel.first", "sel.last")
                    if selected_text:
                        event.widget.clipboard_clear()
                        event.widget.clipboard_append(selected_text)
                        event.widget.delete("sel.first", "sel.last")
                except Exception:
                    try:
                        selected_text = event.widget.selection_get()
                        if selected_text:
                            event.widget.clipboard_clear()
                            event.widget.clipboard_append(selected_text)
                            event.widget.delete("sel.first", "sel.last")
                    except Exception:
                        pass
            except Exception:
                pass
            return "break"

    try:
        target.bind("<Control-KeyPress>", handle_control_keys)
    except Exception as e:
        print(f"[Ошибка привязки клавиш]: {e}")

# =====================================================================
# FLASK СЕРВЕР (ПРИЕМ ДАННЫХ ИЗ РАСШИРЕНИЯ)
# =====================================================================
flask_app = Flask(__name__)
CORS(flask_app)
app_instance = None

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    global app_instance
    if not app_instance or not app_instance.is_active:
        return jsonify({"status": "ignored", "reason": "Assistant is offline"}), 200
        
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "reason": "No data received"}), 400
        app_instance.enqueue_vacancy(data)
        return jsonify({"status": "received", "queue_position": app_instance.vacancy_queue.qsize()}), 200
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500

# =====================================================================
# ГЛАВНЫЙ ИНТЕРФЕЙС ПРИЛОЖЕНИЯ
# =====================================================================
class JobHunterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        global app_instance
        app_instance = self
        
        self.is_active = False
        self.server_started = False
        
        # Потокобезопасная очередь для вакансий
        self.vacancy_queue = queue.Queue()
        self.worker_thread = None
        self.stop_worker_event = threading.Event()
        
        # Загружаем конфигурацию
        self.app_config = jh_storage_manager.load_config()
        
        self.title("Job Hunter AI v1.2.0")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG_DARK)
        ctk.set_appearance_mode("dark")
        
        center_window(self, 680, 770)
        force_dark_title_bar(self)
        
        # Протокол чистого закрытия приложения (высвобождает сокеты Flask)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        try:
            if os.path.exists(ICON_PATH):
                self.iconbitmap(ICON_PATH)
        except Exception:
            pass

        self.setup_ui()
        self.load_config_to_ui()

    def on_closing(self):
        """Безопасное и чистое закрытие приложения для предотвращения зомби-процессов и блокировок портов."""
        self.is_active = False
        self.stop_worker_event.set()
        try:
            time.sleep(0.1)
        except Exception:
            pass
        os._exit(0)

    def load_and_resize_logo(self, height_pixels):
        """Загружает логотип и масштабирует его под DPI экрана."""
        try:
            try:
                scaling = self._get_window_scaling()
            except Exception:
                scaling = 1.0

            target_height = int(height_pixels * scaling)
            
            logo_img = None
            if os.path.exists(LOGO_PNG_PATH):
                logo_img = Image.open(LOGO_PNG_PATH)
            elif os.path.exists(ICON_PATH):
                logo_img = Image.open(ICON_PATH)

            if logo_img:
                aspect_ratio = logo_img.width / logo_img.height
                target_width = int(target_height * aspect_ratio)
                logo_img = logo_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                return ctk.CTkImage(
                    light_image=logo_img,
                    dark_image=logo_img,
                    size=(int(target_width / scaling), int(target_height / scaling))
                )
        except Exception as e:
            print(f"[Ошибка загрузки логотипа]: {e}")
        return None

    def setup_ui(self):
        """Создает элементы управления в главном окне."""
        header_container = ctk.CTkFrame(self, fg_color="transparent")
        header_container.pack(pady=(20, 5))
        
        logo_image = self.load_and_resize_logo(38)
        if logo_image:
            logo_lbl = ctk.CTkLabel(header_container, image=logo_image, text="")
            logo_lbl.pack(side="left", padx=(0, 12))
            
        title_lbl = ctk.CTkLabel(
            header_container, 
            text="JOB HUNTER AI", 
            font=("Arial", 24, "bold"), 
            text_color=COLOR_CYAN_NEON
        )
        title_lbl.pack(side="left")
        
        subtitle_lbl = ctk.CTkLabel(
            self, 
            text="Персональный ассистент по автоматизации карьеры", 
            font=("Arial", 12), 
            text_color=COLOR_TEXT_MUTED
        )
        subtitle_lbl.pack(pady=(0, 20))

        name_frame = ctk.CTkFrame(self, fg_color="transparent")
        name_frame.pack(pady=10, padx=30, fill="x")
        
        self.first_name_input = ctk.CTkEntry(
            name_frame, 
            placeholder_text="Имя (например, Иван)", 
            height=45, 
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BG,
            text_color=COLOR_TEXT_LIGHT,
            placeholder_text_color=COLOR_TEXT_MUTED
        )
        self.first_name_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        bind_russian_hotkeys(self.first_name_input)
        
        self.last_name_input = ctk.CTkEntry(
            name_frame, 
            placeholder_text="Фамилия (например, Иванов)", 
            height=45, 
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BG,
            text_color=COLOR_TEXT_LIGHT,
            placeholder_text_color=COLOR_TEXT_MUTED
        )
        self.last_name_input.pack(side="right", fill="x", expand=True, padx=(10, 0))
        bind_russian_hotkeys(self.last_name_input)

        resume_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        resume_header_frame.pack(anchor="w", padx=30, pady=(15, 5), fill="x")
        
        resume_lbl = ctk.CTkLabel(
            resume_header_frame, 
            text="Ваш опыт работы и навыки (для генерации писем):", 
            font=("Arial", 13, "bold"), 
            text_color=COLOR_TEXT_LIGHT
        )
        resume_lbl.pack(side="left")
        
        def paste_to_resume():
            try:
                clipboard_text = self.clipboard_get()
                self.resume_input.delete("0.0", "end")
                self.resume_input.insert("0.0", clipboard_text.strip())
            except Exception:
                pass

        self.btn_ai_settings = ctk.CTkButton(
            resume_header_frame, 
            text="⚙ Настройки ИИ", 
            width=115, 
            height=26, 
            font=("Arial", 11, "bold"), 
            fg_color=COLOR_CARD_BG, 
            hover_color=COLOR_INPUT_BG, 
            text_color=COLOR_CYAN_NEON,
            border_width=1,
            border_color=COLOR_CYAN_NEON,
            command=self.open_ai_settings_window
        )
        self.btn_ai_settings.pack(side="right", padx=(10, 0))

        self.btn_paste_resume = ctk.CTkButton(
            resume_header_frame, 
            text="Вставить 📋", 
            width=95, 
            height=26, 
            font=("Arial", 11, "bold"), 
            fg_color=COLOR_CYAN_NEON, 
            hover_color=COLOR_CYAN_HOVER, 
            text_color=COLOR_BG_DARK,
            command=paste_to_resume
        )
        self.btn_paste_resume.pack(side="right")
        
        self.resume_input = ctk.CTkTextbox(
            self, 
            height=180, 
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BG,
            border_width=1,
            text_color=COLOR_TEXT_LIGHT
        )
        self.resume_input.pack(pady=5, padx=30, fill="x")
        bind_russian_hotkeys(self.resume_input)

        filter_lbl = ctk.CTkLabel(
            self, 
            text="Первичный автоматический отсев:", 
            font=("Arial", 13, "bold"), 
            text_color=COLOR_TEXT_LIGHT
        )
        filter_lbl.pack(anchor="w", padx=30, pady=(15, 5))
        
        # Контейнер для фильтров
        filter_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=8)
        filter_frame.pack(pady=5, padx=30, fill="x")
        
        # КОРРЕКТНЫЕ И СТАБИЛЬНЫЕ НАСТРОЙКИ ЧЕКБОКСОВ (Размер 20х20 исключает оверлап текстуры)
        self.cb_remote = ctk.CTkCheckBox(
            filter_frame, 
            text="Удаленка", 
            text_color=COLOR_TEXT_LIGHT, 
            fg_color=COLOR_CYAN_NEON,
            hover_color=COLOR_CYAN_HOVER,
            border_color=COLOR_TEXT_MUTED,
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            checkmark_color=COLOR_TEXT_LIGHT
        )
        self.cb_remote.pack(side="left", padx=15, pady=12)
        self.cb_remote.select()
        
        self.cb_office = ctk.CTkCheckBox(
            filter_frame, 
            text="Офис", 
            text_color=COLOR_TEXT_LIGHT, 
            fg_color=COLOR_CYAN_NEON,
            hover_color=COLOR_CYAN_HOVER,
            border_color=COLOR_TEXT_MUTED,
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            checkmark_color=COLOR_TEXT_LIGHT
        )
        self.cb_office.pack(side="left", padx=15, pady=12)
        
        self.cb_hybrid = ctk.CTkCheckBox(
            filter_frame, 
            text="Гибрид", 
            text_color=COLOR_TEXT_LIGHT, 
            fg_color=COLOR_CYAN_NEON,
            hover_color=COLOR_CYAN_HOVER,
            border_color=COLOR_TEXT_MUTED,
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            checkmark_color=COLOR_TEXT_LIGHT
        )
        self.cb_hybrid.pack(side="left", padx=15, pady=12)
        
        self.cb_no_rf = ctk.CTkCheckBox(
            filter_frame, 
            text="Без привязки к РФ 🌐", 
            text_color=COLOR_TEXT_LIGHT, 
            fg_color=COLOR_CYAN_NEON,
            hover_color=COLOR_CYAN_HOVER,
            border_color=COLOR_TEXT_MUTED,
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            checkmark_color=COLOR_TEXT_LIGHT
        )
        self.cb_no_rf.pack(side="right", padx=15, pady=12)
        self.cb_no_rf.select()

        # Важнейший фикс: сброс фокуса при клике на чекбоксы для предотвращения залипания подсветки
        def reset_widget_focus(event):
            self.focus()

        self.cb_remote.bind("<ButtonRelease-1>", reset_widget_focus)
        self.cb_office.bind("<ButtonRelease-1>", reset_widget_focus)
        self.cb_hybrid.bind("<ButtonRelease-1>", reset_widget_focus)
        self.cb_no_rf.bind("<ButtonRelease-1>", reset_widget_focus)

        self.status_lbl = ctk.CTkLabel(
            self, 
            text="● Конфигурация успешно загружена", 
            font=("Arial", 12, "bold"), 
            text_color=COLOR_CYAN_NEON, 
            wraplength=600
        )
        self.status_lbl.pack(pady=10)

        self.btn_toggle = ctk.CTkButton(
            self, 
            text="ЗАПУСТИТЬ АССИСТЕНТА", 
            font=("Arial", 15, "bold"), 
            fg_color=COLOR_CYAN_NEON, 
            hover_color=COLOR_CYAN_HOVER, 
            text_color=COLOR_BG_DARK,
            height=50, 
            command=self.toggle_assistant
        )
        self.btn_toggle.pack(pady=5, padx=30, fill="x")
        
        btn_open_results = ctk.CTkButton(
            self, 
            text="📁 ОТКРЫТЬ ОДОБРЕННЫЕ ВАКАНСИИ (ОТОБРАНО)", 
            font=("Arial", 13, "bold"), 
            fg_color=COLOR_GOLD, 
            hover_color=COLOR_GOLD_HOVER, 
            text_color=COLOR_BG_DARK,
            height=45, 
            command=self.open_results
        )
        btn_open_results.pack(pady=(5, 20), padx=30, fill="x")

    def show_api_help(self):
        """Отображает красивое диалоговое окно-справку с информацией о бесплатных ключах."""
        help_win = ctk.CTkToplevel(self)
        help_win.withdraw()
        help_win.title("Где взять бесплатный API ключ?")
        help_win.configure(fg_color=COLOR_BG_DARK)
        
        force_dark_title_bar(help_win)
        
        try:
            if os.path.exists(ICON_PATH):
                help_win.after(200, lambda: help_win.iconbitmap(ICON_PATH))
        except Exception:
            pass
            
        center_window(help_win, 460, 260, self)
        
        help_win.grab_set()
        help_win.focus_force()

        lbl_title = ctk.CTkLabel(
            help_win, 
            text="🔑 API-ключ Gemini бесплатно за 1 минуту", 
            font=("Arial", 14, "bold"), 
            text_color=COLOR_CYAN_NEON
        )
        lbl_title.pack(pady=(20, 10))

        help_text = (
            "Для провайдера Gemini вы можете получить официальный\n"
            "высокоскоростной API-ключ абсолютно бесплатно.\n\n"
            "1. Перейдите по ссылке в Google AI Studio.\n"
            "2. Нажмите кнопку 'Get API Key'.\n"
            "3. Скопируйте и вставьте в настройки Job Hunter AI."
        )
        lbl_content = ctk.CTkLabel(
            help_win, 
            text=help_text, 
            font=("Arial", 11), 
            text_color=COLOR_TEXT_LIGHT, 
            justify="left"
        )
        lbl_content.pack(padx=25, pady=5)

        btn_go = ctk.CTkButton(
            help_win, 
            text="Получить ключ в Google AI Studio 🌐", 
            font=("Arial", 11, "bold"),
            fg_color=COLOR_CYAN_NEON, 
            hover_color=COLOR_CYAN_HOVER, 
            text_color=COLOR_BG_DARK,
            height=36,
            command=lambda: webbrowser.open("https://aistudio.google.com/")
        )
        btn_go.pack(pady=(15, 5))

    def open_ai_settings_window(self):
        """Создает модальное дочернее окно для настройки параметров и провайдеров ИИ."""
        settings_win = ctk.CTkToplevel(self)
        settings_win.withdraw()  
        settings_win.title("Параметры ИИ и Задержки")
        settings_win.configure(fg_color=COLOR_BG_DARK)
        
        try:
            if os.path.exists(ICON_PATH):
                settings_win.after(200, lambda: settings_win.iconbitmap(ICON_PATH))
            else:
                settings_win.after(200, lambda: settings_win.iconbitmap(sys.executable))
        except Exception:
            pass
        
        force_dark_title_bar(settings_win)
        center_window(settings_win, 450, 520, self) 
        
        settings_win.grab_set()
        settings_win.focus_force()

        title_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        title_frame.pack(pady=(15, 10), padx=30, fill="x")
        title_frame.columnconfigure(0, weight=1)
        title_frame.columnconfigure(1, weight=0)

        set_title = ctk.CTkLabel(
            title_frame, 
            text="⚙ НАСТРОЙКИ AI ENGINE", 
            font=("Arial", 16, "bold"), 
            text_color=COLOR_CYAN_NEON
        )
        set_title.grid(row=0, column=0, sticky="w")

        btn_help_icon = ctk.CTkButton(
            title_frame, 
            text="❔ Помощь", 
            font=("Arial", 11, "bold"), 
            text_color=COLOR_CYAN_NEON,
            fg_color="transparent",
            hover_color=COLOR_INPUT_BG,
            width=75,
            height=25,
            command=self.show_api_help
        )
        btn_help_icon.grid(row=0, column=1, sticky="e")

        prov_lbl = ctk.CTkLabel(settings_win, text="Активный провайдер ИИ:", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_LIGHT)
        prov_lbl.pack(anchor="w", padx=30, pady=(5, 2))

        model_checkboxes = []
        model_group_frame = ctk.CTkFrame(settings_win, fg_color=COLOR_CARD_BG, corner_radius=8)

        temp_api_keys = self.app_config.get("api_keys", {}).copy()
        current_prov_var = ctk.StringVar(value=self.app_config.get("current_provider", "Gemini"))

        def on_provider_changed(new_provider):
            old_provider = self.app_config.get("current_provider", "Gemini")
            temp_api_keys[old_provider] = api_key_entry.get().strip()
            
            self.app_config["current_provider"] = new_provider
            
            api_key_entry.delete(0, "end")
            api_key_entry.insert(0, temp_api_keys.get(new_provider, ""))
            
            for cb in model_checkboxes:
                cb.destroy()
            model_checkboxes.clear()

            available_models = ALL_PROVIDERS_MODELS.get(new_provider, [])
            active_list = self.app_config["active_models"].get(new_provider, [])
            
            for m_name in available_models:
                cb_var = ctk.BooleanVar(value=(m_name in active_list))
                cb = ctk.CTkCheckBox(
                    model_group_frame, 
                    text=m_name, 
                    variable=cb_var,
                    text_color=COLOR_TEXT_LIGHT, 
                    fg_color=COLOR_CYAN_NEON,
                    hover_color=COLOR_CYAN_HOVER,
                    border_color=COLOR_TEXT_MUTED,
                    checkbox_width=20,
                    checkbox_height=20,
                    border_width=2,
                    checkmark_color=COLOR_TEXT_LIGHT,
                    command=lambda name=m_name, var=cb_var: update_active_models(new_provider, name, var.get())
                )
                cb.pack(anchor="w", padx=15, pady=6)
                model_checkboxes.append(cb)

        def update_active_models(provider, name, is_selected):
            if provider not in self.app_config["active_models"]:
                self.app_config["active_models"][provider] = []
            
            curr_active = self.app_config["active_models"][provider]
            if is_selected and name not in curr_active:
                curr_active.append(name)
            elif not is_selected and name in curr_active:
                curr_active.remove(name)

        provider_dropdown = ctk.CTkOptionMenu(
            settings_win,
            values=["Gemini", "OpenAI", "Anthropic", "DeepSeek"],
            variable=current_prov_var,
            command=on_provider_changed,
            fg_color=COLOR_CARD_BG,
            button_color=COLOR_INPUT_BG,
            button_hover_color=COLOR_CARD_BG,
            text_color=COLOR_TEXT_LIGHT,
            dropdown_fg_color=COLOR_CARD_BG,
            dropdown_hover_color=COLOR_INPUT_BG,
            dropdown_text_color=COLOR_TEXT_LIGHT
        )
        provider_dropdown.pack(pady=(2, 10), padx=30, fill="x")

        key_lbl = ctk.CTkLabel(settings_win, text="API Ключ провайдера:", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_LIGHT)
        key_lbl.pack(anchor="w", padx=30, pady=(5, 2))

        api_key_entry = ctk.CTkEntry(
            settings_win, 
            height=40,
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BG,
            text_color=COLOR_TEXT_LIGHT,
            placeholder_text="Вставьте ключ доступа...",
            show="*"
        )
        api_key_entry.pack(pady=(2, 10), padx=30, fill="x")
        bind_russian_hotkeys(api_key_entry)

        model_lbl = ctk.CTkLabel(settings_win, text="Приоритетные модели каскада:", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_LIGHT)
        model_lbl.pack(anchor="w", padx=30, pady=(5, 2))

        model_group_frame.pack(pady=(2, 15), padx=30, fill="x")

        api_key_entry.insert(0, temp_api_keys.get(current_prov_var.get(), ""))
        on_provider_changed(current_prov_var.get())

        delay_lbl_var = ctk.StringVar()
        
        def update_delay_label(val):
            delay_lbl_var.set(f"Защитная пауза API: {int(float(val))} сек.")

        current_delay = self.app_config.get("request_delay", 15)
        
        delay_info_lbl = ctk.CTkLabel(settings_win, textvariable=delay_lbl_var, font=("Arial", 12, "bold"), text_color=COLOR_TEXT_LIGHT)
        delay_info_lbl.pack(anchor="w", padx=30, pady=(5, 2))
        
        update_delay_label(current_delay)

        delay_slider = ctk.CTkSlider(
            settings_win,
            from_=0,
            to=60,
            number_of_steps=60,
            command=update_delay_label,
            button_color=COLOR_CYAN_NEON,
            button_hover_color=COLOR_CYAN_HOVER,
            progress_color=COLOR_CYAN_NEON,
            fg_color=COLOR_INPUT_BG
        )
        delay_slider.pack(pady=(2, 15), padx=30, fill="x")
        delay_slider.set(current_delay)

        def save_and_close():
            active_prov = current_prov_var.get()
            temp_api_keys[active_prov] = api_key_entry.get().strip()
            
            self.app_config["current_provider"] = active_prov
            self.app_config["api_keys"] = temp_api_keys
            self.app_config["request_delay"] = int(delay_slider.get())
            
            jh_storage_manager.save_config(self.app_config)
            self.update_status("● Конфигурация успешно сохранена", COLOR_CYAN_NEON)
            settings_win.destroy()

        btn_save = ctk.CTkButton(
            settings_win,
            text="СОХРАНИТЬ И ЗАКРЫТЬ",
            font=("Arial", 13, "bold"),
            fg_color=COLOR_CYAN_NEON,
            hover_color=COLOR_CYAN_HOVER,
            text_color=COLOR_BG_DARK,
            height=40,
            command=save_and_close
        )
        btn_save.pack(pady=(5, 15), padx=30, fill="x")

    def load_config_to_ui(self):
        """Загружает сохраненные настройки пользователя в основные поля UI при запуске."""
        self.first_name_input.delete(0, "end")
        self.first_name_input.insert(0, self.app_config.get("first_name", ""))
        
        self.last_name_input.delete(0, "end")
        self.last_name_input.insert(0, self.app_config.get("last_name", ""))
        
        self.resume_input.delete("0.0", "end")
        self.resume_input.insert("0.0", self.app_config.get("resume", ""))
        
        if not self.app_config.get("filter_remote", True): self.cb_remote.deselect()
        if self.app_config.get("filter_office", False): self.cb_office.select()
        if self.app_config.get("filter_hybrid", False): self.cb_hybrid.select()
        if not self.app_config.get("filter_no_rf", True): self.cb_no_rf.deselect()

    def save_current_config(self):
        """Синхронизирует текущие введенные настройки UI с конфигом и пишет их на диск."""
        self.app_config["first_name"] = self.first_name_input.get().strip()
        self.app_config["last_name"] = self.last_name_input.get().strip()
        self.app_config["resume"] = self.resume_input.get("0.0", "end-1c").strip()
        self.app_config["filter_remote"] = bool(self.cb_remote.get())
        self.app_config["filter_office"] = bool(self.cb_office.get())
        self.app_config["filter_hybrid"] = bool(self.cb_hybrid.get())
        self.app_config["filter_no_rf"] = bool(self.cb_no_rf.get())
        
        jh_storage_manager.save_config(self.app_config)

    def set_inputs_state(self, state):
        """Управляет доступностью полей конфигурации во время работы ассистента."""
        self.first_name_input.configure(state=state)
        self.last_name_input.configure(state=state)
        self.resume_input.configure(state=state)
        self.btn_paste_resume.configure(state=state)
        self.btn_ai_settings.configure(state=state)
        self.cb_remote.configure(state=state)
        self.cb_office.configure(state=state)
        self.cb_hybrid.configure(state=state)
        self.cb_no_rf.configure(state=state)

    def toggle_assistant(self):
        """Включает/выключает прием вебхуков и работу ИИ."""
        if not self.is_active:
            self.app_config = jh_storage_manager.load_config()
            
            provider = self.app_config.get("current_provider", "Gemini")
            api_key = self.app_config.get("api_keys", {}).get(provider, "").strip()
            first_name = self.first_name_input.get().strip()
            
            if not api_key:
                messagebox.showerror(
                    "Ошибка запуска", 
                    f"Пожалуйста, введите ваш API Ключ для провайдера {provider} в окне 'Настройки ИИ'.",
                    parent=self
                )
                return
            if not first_name:
                messagebox.showerror(
                    "Ошибка запуска", 
                    "Пожалуйста, укажите ваше имя (оно используется для генерации писем).",
                    parent=self
                )
                return

            self.save_current_config()
            self.is_active = True
            
            self.set_inputs_state("disabled")
            
            self.btn_toggle.configure(text="ОТКЛЮЧИТЬ АССИСТЕНТА", fg_color=COLOR_RED, hover_color=COLOR_RED_HOVER, text_color=COLOR_TEXT_LIGHT)
            self.status_lbl.configure(text="● Ассистент активен. Ожидание вакансий...", text_color=COLOR_CYAN_NEON)
            
            while not self.vacancy_queue.empty():
                try:
                    self.vacancy_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.stop_worker_event.clear()
            self.worker_thread = threading.Thread(target=self.queue_worker_loop, daemon=True)
            self.worker_thread.start()
            
            if not self.server_started:
                self.server_started = True
                threading.Thread(target=self.run_flask_server, daemon=True).start()
        else:
            self.is_active = False
            self.stop_worker_event.set()
            
            self.set_inputs_state("normal")
            
            self.btn_toggle.configure(text="ЗАПУСТИТЬ АССИСТЕНТА", fg_color=COLOR_CYAN_NEON, hover_color=COLOR_CYAN_HOVER, text_color=COLOR_BG_DARK)
            self.status_lbl.configure(text="● Ассистент отключен", text_color=COLOR_RED)

    def kill_process_on_port(self, port):
        """Принудительно завершает процесс, занимающий указанный порт (работает на Windows)."""
        try:
            import subprocess
            import os
            cmd = f'netstat -ano | findstr :{port}'
            output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            pids = set()
            for line in output.splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and f":{port}" in parts[1]:
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) != os.getpid():
                        pids.add(int(pid))
            for pid in pids:
                print(f"[Система]: Обнаружен зомби-процесс {pid} на порту {port}. Принудительно завершаем...")
                subprocess.run(f'taskkill /F /PID {pid}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[Система]: Не удалось очистить порт {port}: {e}")

    def run_flask_server(self):
        """Запускает Flask-сервер принудительно на порту 5000, предварительно очищая его от зомби-процессов."""
        port = 5000
        self.kill_process_on_port(port)
        try:
            flask_app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)
        except Exception as e:
            print(f"[Flask Ошибка]: Не удалось привязать сокет к порту {port}: {e}")
            self.update_status(f"⚠ Сбой веб-сервера на порту {port}. Закройте другие копии программы.", COLOR_RED)

    def update_status(self, text, color):
        """Безопасное обновление статуса на главном экране из фоновых потоков."""
        try:
            if self.winfo_exists():
                self.after(0, lambda: self.status_lbl.configure(text=text, text_color=color))
        except Exception as e:
            print(f"[Thread Status Error]: {e}")

    def enqueue_vacancy(self, data):
        """Добавляет входящую вакансию в очередь и обновляет счетчик"""
        self.vacancy_queue.put(data)
        q_size = self.vacancy_queue.qsize()
        self.update_status(f"● Входящая вакансия добавлена в очередь (всего в очереди: {q_size})", COLOR_GOLD)

    def queue_worker_loop(self):
        """Фоновый цикл обработки очереди с динамической задержкой из настроек."""
        while not self.stop_worker_event.is_set():
            try:
                vacancy_data = self.vacancy_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            initial_q_size = self.vacancy_queue.qsize() + 1
            delay_seconds = self.app_config.get("request_delay", 15)

            for remaining in range(delay_seconds, 0, -1):
                if self.stop_worker_event.is_set():
                    return
                current_q_size = self.vacancy_queue.qsize() + 1
                self.update_status(
                    f"● Пауза {remaining} сек для защиты лимитов API (в очереди: {current_q_size})", 
                    COLOR_GOLD
                )
                time.sleep(1)

            if not self.stop_worker_event.is_set():
                self.process_incoming_vacancy(vacancy_data)
                self.vacancy_queue.task_done()

    def process_incoming_vacancy(self, vacancy_data):
        """Обработка одной вакансии через ИИ-движок"""
        self.update_status("● ИИ анализирует прилетевшую вакансию...", COLOR_GOLD)
        self.app_config = jh_storage_manager.load_config()

        try:
            status, result_text, extracted_info = jh_ai_engine.analyze_and_generate(vacancy_data, self.app_config)
            
            company = extracted_info.get("company", vacancy_data.get("company", "Не указана"))
            title = extracted_info.get("title", vacancy_data.get("title", "Не указано"))
            url = vacancy_data.get("url", "#")
            description = vacancy_data.get("text", "")

            if status == "APPROVED":
                jh_storage_manager.save_approved_vacancy(
                    company=company,
                    title=title,
                    url=url,
                    cover_letter=result_text,
                    description=description
                )
                self.update_status(f"✓ ОДОБРЕНО: {title} в {company}!", COLOR_CYAN_NEON)
            elif status == "REJECTED":
                jh_storage_manager.save_rejected_vacancy(
                    company=company,
                    title=title,
                    url=url,
                    reason=result_text
                )
                self.update_status(f"✕ Отклонено ИИ: {title} в {company} (причина в результатах)", COLOR_RED)
            else:
                self.update_status(f"⚠ Сбой ИИ: {result_text}", COLOR_RED)
        except Exception as e:
            self.update_status(f"⚠ Сбой обработки: {str(e)}", COLOR_RED)

    def open_results(self):
        """Открывает окно со списком одобренных ИИ вакансий"""
        jh_results_ui.open_window(self)

# =====================================================================
# СТАРТ ПРИЛОЖЕНИЯ
# =====================================================================
if __name__ == "__main__":
    app = JobHunterApp()
    app.mainloop()