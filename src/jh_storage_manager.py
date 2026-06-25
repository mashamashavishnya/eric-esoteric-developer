import json
import os

# Путь к системной папке AppData\Roaming для текущего пользователя Windows.
APPDATA_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'Job Hunter AI')

# Автоматически создаем папку "Job Hunter AI" в AppData, если её ещё нет на компьютере.
os.makedirs(APPDATA_DIR, exist_ok=True)

# Указываем абсолютные безопасные пути к файлам баз данных вакансий и конфигурации.
APPROVED_FILE = os.path.join(APPDATA_DIR, "saved_vacancies.json")
REJECTED_FILE = os.path.join(APPDATA_DIR, "rejected_vacancies.json")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")

def init_db():
    """Создает пустые файлы баз данных, если они отсутствуют."""
    if not os.path.exists(APPROVED_FILE):
        _save_file(APPROVED_FILE, [])
    if not os.path.exists(REJECTED_FILE):
        _save_file(REJECTED_FILE, [])

def _load_file(filepath):
    """Безопасно загружает данные из JSON файла."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_file(filepath, data):
    """Записывает данные в файл в формате UTF-8."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[Ошибка сохранения]: Не удалось записать файл {filepath}. Причина: {e}")

def load_config():
    """Безопасно загружает расширенную конфигурацию приложения с дефолтными значениями."""
    default_config = {
        "first_name": "",
        "last_name": "",
        "resume": "",
        "filter_remote": True,
        "filter_office": False,
        "filter_hybrid": False,
        "filter_no_rf": True,
        "current_provider": "Gemini",
        "api_keys": {
            "Gemini": "",
            "OpenAI": "",
            "Anthropic": "",
            "DeepSeek": ""
        },
        "active_models": {
            "Gemini": ["gemini-3.1-flash-lite", "gemini-3.5-flash"],
            "OpenAI": ["gpt-5-mini"],
            "Anthropic": ["claude-4-haiku"],
            "DeepSeek": ["deepseek-chat"]
        },
        "request_delay": 15
    }
    
    if not os.path.exists(CONFIG_FILE):
        _save_file(CONFIG_FILE, default_config)
        return default_config
        
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_config = json.load(f)
            # Бережно обновляем отсутствующие ключи в пользовательском конфиге
            for key, val in default_config.items():
                if key not in user_config:
                    user_config[key] = val
                elif isinstance(val, dict) and isinstance(user_config[key], dict):
                    for sub_key, sub_val in val.items():
                        if sub_key not in user_config[key]:
                            user_config[key][sub_key] = sub_val
            
            # Автоматическая миграция устаревших моделей Gemini на 2026 год
            if "active_models" in user_config and "Gemini" in user_config["active_models"]:
                gemini_active = user_config["active_models"]["Gemini"]
                migrated = False
                for idx, model in enumerate(gemini_active):
                    if model == "gemini-3.1-flash":
                        gemini_active[idx] = "gemini-3.1-flash-lite"
                        migrated = True
                    elif model == "gemini-3.0-pro":
                        gemini_active[idx] = "gemini-3.1-pro"
                        migrated = True
                if migrated:
                    seen = set()
                    user_config["active_models"]["Gemini"] = [x for x in gemini_active if not (x in seen or seen.add(x))]
                    _save_file(CONFIG_FILE, user_config)
                    print("[Сборщик-Миграция]: Конфигурация Gemini успешно обновлена.")
                    
            return user_config
    except Exception:
        return default_config

def save_config(config_data):
    """Сохраняет конфигурацию приложения в AppData."""
    _save_file(CONFIG_FILE, config_data)

def save_approved_vacancy(company, title, url, cover_letter="", description=""):
    """Добавляет новую одобренную ИИ вакансию в список."""
    vacancies = _load_file(APPROVED_FILE)
    new_vacancy = {
        "company": company,
        "title": title,
        "url": url,
        "description": description,
        "cover_letter": cover_letter
    }
    vacancies.append(new_vacancy)
    _save_file(APPROVED_FILE, vacancies)

def save_rejected_vacancy(company, title, url, reason=""):
    """Добавляет отклоненную вакансию в журнал (макс 50 записей)."""
    vacancies = _load_file(REJECTED_FILE)
    new_vacancy = {
        "company": company,
        "title": title,
        "url": url,
        "reason": reason
    }
    vacancies.append(new_vacancy)
    if len(vacancies) > 50:
        vacancies = vacancies[-50:]
    _save_file(REJECTED_FILE, vacancies)

def get_all_approved():
    """Возвращает список всех сохраненных вакансий."""
    return _load_file(APPROVED_FILE)

def get_all_rejected():
    """Возвращает список всех отклоненных вакансий."""
    return _load_file(REJECTED_FILE)

def delete_vacancy_by_url(url):
    """Удаляет конкретную одобренную вакансию из списка по её ссылке."""
    vacancies = _load_file(APPROVED_FILE)
    vacancies = [v for v in vacancies if v.get('url') != url]
    _save_file(APPROVED_FILE, vacancies)

def delete_rejected_by_url(url):
    """Удаляет конкретную отклоненную вакансию по её ссылке."""
    vacancies = _load_file(REJECTED_FILE)
    vacancies = [v for v in vacancies if v.get('url') != url]
    _save_file(REJECTED_FILE, vacancies)

def clear_all_vacancies():
    """Полностью очищает базу данных одобренных."""
    _save_file(APPROVED_FILE, [])

def clear_all_rejected():
    """Полностью очищает базу данных отклоненных."""
    _save_file(REJECTED_FILE, [])