# results_ui.py
import os
import sys
import customtkinter as ctk
import storage_manager
from tkinter import messagebox

# Получаем абсолютный путь к папке проекта, чтобы иконка не терялась
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "icon.ico")

def force_dark_title_bar(window):
    """Принудительно красит заголовок окна в темный цвет Windows"""
    try:
        import ctypes
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if hwnd == 0: hwnd = window.winfo_id()
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(ctypes.c_int(1)), 4)
    except Exception:
        pass

def set_window_icon(window):
    """Безопасная установка иконки программы"""
    try:
        if os.path.exists(ICON_PATH):
            window.after(200, lambda: window.iconbitmap(ICON_PATH))
        else:
            window.after(200, lambda: window.iconbitmap(sys.executable))
    except Exception:
        pass

def center_window(window, width, height, parent=None):
    """
    Полностью стабильная функция центрирования окон для High-DPI экранов.
    Предотвращает смещение и уплывание окон из-за повторного масштабирования в Windows.
    Рассчитывает физические координаты экрана для идеально точной стыковки.
    """
    try:
        window.attributes("-alpha", 0.0)
    except Exception:
        pass
    
    def _apply_centered_position():
        if not window.winfo_exists():
            return
        
        try:
            # Заставляем систему обновить геометрию перед расчетами
            window.update_idletasks()
            
            # Безопасно получаем масштаб через приватный метод инстанса CTk
            try:
                scaling = window._get_window_scaling()
                if not scaling or scaling <= 0:
                    scaling = 1.0
            except Exception:
                scaling = 1.0

            scaled_width = int(width * scaling)
            scaled_height = int(height * scaling)

            if parent and parent.winfo_exists():
                # Находим физические координаты родительского окна на экране
                parent_x = parent.winfo_x()
                parent_y = parent.winfo_y()
                parent_w = parent.winfo_width()
                parent_h = parent.winfo_height()
                
                # Рассчитываем точный центр относительно родительского окна
                x = parent_x + (parent_w - scaled_width) // 2
                y = parent_y + (parent_h - scaled_height) // 2
            else:
                # Если родителя нет, берем физический размер всего экрана монитора
                screen_width = window.winfo_screenwidth()
                screen_height = window.winfo_screenheight()
                
                x = (screen_width - scaled_width) // 2
                y = (screen_height - scaled_height) // 2
            
            # Защита от улета за левый и верхний края монитора
            x = max(0, int(x))
            y = max(0, int(y))
            
            # Устанавливаем геометрию (физические пиксели позиционирования)
            window.geometry(f"{width}x{height}+{x}+{y}")
            
        except Exception as e:
            print(f"[Ошибка центрирования]: {e}")
            window.geometry(f"{width}x{height}")
        finally:
            # Гарантируем возврат видимости окну в любом случае!
            try:
                window.attributes("-alpha", 1.0)
                window.deiconify()
            except Exception:
                pass
        
    window.after(100, _apply_centered_position)

def open_window(parent_window):
    """Создает независимое окно со списком одобренных и отклоненных вакансий"""
    window = ctk.CTkToplevel(parent_window)
    window.title("Результаты анализа ИИ")
    
    # Применяем стили заголовка и иконку
    force_dark_title_bar(window)
    set_window_icon(window)
    
    # Помещаем окно результатов ровно по центру главного окна приложения
    center_window(window, 680, 750, parent_window)
    
    window.lift()
    window.focus_force()
    window.attributes("-topmost", True)
    window.after(500, lambda: window.attributes("-topmost", False))

    window.last_approved_count = -1
    window.last_rejected_count = -1
    window.current_tab = "APPROVED"  # Текущая выбранная вкладка: "APPROVED" или "REJECTED"

    # Скроллируемая область для карточек
    scroll_frame = ctk.CTkScrollableFrame(window, width=640, height=520, fg_color="#1A1D1A")

    def segment_changed(value):
        if "Одобренные" in value:
            window.current_tab = "APPROVED"
            btn_clear_all.configure(text="🗑️ Очистить список одобренных", fg_color="#EF4444", hover_color="#DC2626")
        else:
            window.current_tab = "REJECTED"
            btn_clear_all.configure(text="🗑️ Очистить журнал отклонений", fg_color="#374151", hover_color="#4B5563")
        refresh_list(force=True)

    # Переключатель вкладок
    tab_segment = ctk.CTkSegmentedButton(
        window, values=["Одобренные ИИ 👍", "Отклоненные ИИ ✕"], 
        font=("Arial", 13, "bold"), command=segment_changed,
        selected_color="#10B981", selected_hover_color="#059669"
    )
    tab_segment.pack(pady=(15, 5), padx=20, fill="x")
    tab_segment.set("Одобренные ИИ 👍")

    scroll_frame.pack(pady=10, padx=15, fill="both", expand=True)

    def refresh_list(force=False):
        """Перерисовывает список вакансий из файлов на лету"""
        if not window.winfo_exists():
            return

        try:
            approved = storage_manager.get_all_approved()
            rejected = storage_manager.get_all_rejected()
        except Exception as e:
            print(f"[Ошибка чтения БД]: {e}")
            approved = []
            rejected = []

        # Обновляем счетчики на вкладках
        tab_segment.configure(values=[f"Одобренные ИИ ({len(approved)}) 👍", f"Отклоненные ИИ ({len(rejected)}) ✕"])

        # Проверка изменений
        if not force and len(approved) == window.last_approved_count and len(rejected) == window.last_rejected_count:
            return

        window.last_approved_count = len(approved)
        window.last_rejected_count = len(rejected)

        for widget in scroll_frame.winfo_children():
            widget.destroy()

        vacancies = approved if window.current_tab == "APPROVED" else rejected

        if not vacancies:
            empty_text = "Список пуст. Одобренных вакансий пока нет." if window.current_tab == "APPROVED" else "Журнал отклонений пуст."
            empty_lbl = ctk.CTkLabel(scroll_frame, text=empty_text, font=("Arial", 14), text_color="#6B7280")
            empty_lbl.pack(pady=50)
            btn_clear_all.configure(state="disabled")
            return

        btn_clear_all.configure(state="normal")

        for item in vacancies:
            company = item.get("company", "Не указана")
            title = item.get("title", "Не указано")
            url = item.get("url", "#")

            card = ctk.CTkFrame(scroll_frame, fg_color="#262A26", corner_radius=8)
            card.pack(pady=6, padx=5, fill="x")

            if window.current_tab == "APPROVED":
                # Одобренная карточка
                cover_letter = item.get("cover_letter", "")
                description = item.get("description", "")
                
                info_text = f"🏢 {company}\n💼 {title}"
                info_lbl = ctk.CTkLabel(
                    card, text=info_text, font=("Arial", 13, "bold"), 
                    anchor="w", justify="left", text_color="#E5E7EB", wraplength=400
                )
                info_lbl.pack(side="left", padx=15, pady=12, fill="x", expand=True)

                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(side="right", padx=10, pady=10)

                btn_open = ctk.CTkButton(
                    btn_frame, text="📄 Показать полностью", width=140, fg_color="#10B981", hover_color="#059669",
                    command=lambda t=title, c=company, cl=cover_letter, d=description: show_details_window(window, t, c, cl, d)
                )
                btn_open.grid(row=0, column=0, padx=5)

                btn_delete = ctk.CTkButton(
                    btn_frame, text="✕", width=32, height=32, corner_radius=6,
                    fg_color="#D94343", hover_color="#B83232",
                    font=("Arial", 12, "bold"),
                    command=lambda u=url: delete_approved_item(u)
                )
                btn_delete.grid(row=0, column=1, padx=5)

            else:
                # Отклоненная карточка с автопереносом длинной причины отказа!
                reason = item.get("reason", "Причина не указана")
                
                info_text = f"🏢 {company} | 💼 {title}\n"
                info_lbl = ctk.CTkLabel(
                    card, text=info_text, font=("Arial", 13, "bold"), 
                    anchor="w", justify="left", text_color="#EF4444"
                )
                info_lbl.pack(anchor="w", padx=15, pady=(10, 2))

                reason_lbl = ctk.CTkLabel(
                    card, text=f"✕ {reason}", font=("Arial", 12),
                    anchor="w", justify="left", text_color="#9CA3AF", wraplength=580
                )
                reason_lbl.pack(anchor="w", padx=15, pady=(0, 10), fill="x", expand=True)

                # Кнопка удаления для отклоненного элемента
                btn_delete_rej = ctk.CTkButton(
                    card, text="Удалить из истории ✕", width=150, height=26, corner_radius=6,
                    fg_color="#374151", hover_color="#4B5563",
                    font=("Arial", 11),
                    command=lambda u=url: delete_rejected_item(u)
                )
                btn_delete_rej.pack(anchor="e", padx=15, pady=(0, 10))

    def auto_refresh_loop():
        """Фоновый цикл проверки базы данных каждые 3 секунды"""
        if window.winfo_exists():
            refresh_list(force=False)
            window.after(3000, auto_refresh_loop)

    def delete_approved_item(url):
        storage_manager.delete_vacancy_by_url(url)
        refresh_list(force=True)

    def delete_rejected_item(url):
        storage_manager.delete_rejected_by_url(url)
        refresh_list(force=True)

    def clear_all():
        if window.current_tab == "APPROVED":
            if messagebox.askyesno("Очистка базы данных", "Вы уверены, что хотите безвозвратно удалить ВСЕ одобренные вакансии из списка?"):
                storage_manager.clear_all_vacancies()
                refresh_list(force=True)
        else:
            if messagebox.askyesno("Очистка базы данных", "Вы уверены, что хотите очистить весь журнал отклоненных вакансий?"):
                storage_manager.clear_all_rejected()
                refresh_list(force=True)

    # Кнопка полной очистки базы данных
    bottom_frame = ctk.CTkFrame(window, fg_color="transparent")
    bottom_frame.pack(pady=15, fill="x", padx=20)

    btn_clear_all = ctk.CTkButton(
        bottom_frame, text="🗑️ Очистить список одобренных", fg_color="#EF4444", hover_color="#DC2626", 
        command=clear_all, height=40, font=("Arial", 13, "bold")
    )
    btn_clear_all.pack(side="right")

    # Первичный рендеринг и запуск фонового обновления
    refresh_list(force=True)
    auto_refresh_loop()


def show_details_window(parent, title, company, cover_letter, description):
    """Детальное окно просмотра вакансии и сопроводительного письма (как на скриншотах 2 и 3)"""
    top = ctk.CTkToplevel(parent)
    top.title("Полная информация о вакансии")
    
    force_dark_title_bar(top)
    set_window_icon(top)
    
    # Центрируем детальное окно ровно по центру окна списка
    center_window(top, 700, 800, parent)
    
    top.lift()
    top.focus_force()
    top.attributes("-topmost", True)
    top.after(400, lambda: top.attributes("-topmost", False))
    
    # Крупный центрированный заголовок с названием вакансии и компании (выделен зеленым цветом)
    header_text = f"{title}\nРаботодатель: {company}"
    header_label = ctk.CTkLabel(
        top, text=header_text, font=("Arial", 16, "bold"), 
        text_color="#10B981", justify="center", wraplength=640
    )
    header_label.pack(pady=15, padx=20)
    
    # Окно вывода содержимого
    content_box = ctk.CTkTextbox(top, font=("Arial", 13), width=640, height=500, fg_color="#262A26")
    content_box.pack(pady=10, padx=20)
    
    def show_desc():
        btn_desc.configure(fg_color="#10B981", hover_color="#059669")
        btn_letter.configure(fg_color="#374151", hover_color="#4B5563")
        content_box.delete("0.0", "end")
        content_box.insert("0.0", description if description else "Текст вакансии отсутствует.")

    def show_letter():
        btn_letter.configure(fg_color="#10B981", hover_color="#059669")
        btn_desc.configure(fg_color="#374151", hover_color="#4B5563")
        content_box.delete("0.0", "end")
        content_box.insert("0.0", cover_letter if cover_letter else "Письмо не было сгенерировано.")

    # Вкладки Текст / Письмо
    tab_frame = ctk.CTkFrame(top, fg_color="transparent")
    tab_frame.pack(pady=5)

    btn_desc = ctk.CTkButton(tab_frame, text="📄 Текст вакансии", command=show_desc, width=200, font=("Arial", 12, "bold"))
    btn_desc.grid(row=0, column=0, padx=10)

    btn_letter = ctk.CTkButton(tab_frame, text="✍️ Сопроводительное письмо", command=show_letter, width=200, font=("Arial", 12, "bold"))
    btn_letter.grid(row=0, column=1, padx=10)

    # Кнопка быстрой скопируемости контента в буфер обмена
    def copy_to_clipboard():
        top.clipboard_clear()
        top.clipboard_append(content_box.get("0.0", "end-1c"))
        btn_copy.configure(text="Успешно скопировано! ✓", fg_color="#059669")
        top.after(2000, lambda: btn_copy.configure(text="Копировать содержимое в буфер 📋", fg_color="#10B981"))

    btn_copy = ctk.CTkButton(top, text="Копировать содержимое в буфер 📋", command=copy_to_clipboard, fg_color="#10B981", height=42, font=("Arial", 13, "bold"))
    btn_copy.pack(pady=20)

    # По умолчанию открываем описание вакансии
    show_desc()