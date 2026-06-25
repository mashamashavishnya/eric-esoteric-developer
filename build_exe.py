import os
import sys
import subprocess
import shutil

def run_self_healing_refactor(script_dir):
    """
    Автоматически переименовывает файлы проекта во избежание конфликтов импорта 
    с установленными в системе библиотеками (например, storage_manager) 
    и автоматически обновляет ссылки в коде.
    """
    print("\n[Рефакторинг] Запуск автоматического устранения конфликтов имён (Self-Healing)...")
    src_dir = os.path.join(script_dir, "src")
    if not os.path.exists(src_dir):
        print("[Рефакторинг] Папка src/ не найдена. Пропускаем.")
        return

    # Карта переименования файлов во избежание маскирования системных библиотек
    rename_map = {
        "storage_manager.py": "jh_storage_manager.py",
        "ai_engine.py": "jh_ai_engine.py",
        "results_ui.py": "jh_results_ui.py"
    }

    # 1. Сначала переносим всё из корня в src, если что-то осталось
    for old_name in rename_map.keys():
        root_file = os.path.join(script_dir, old_name)
        if os.path.exists(root_file):
            dest = os.path.join(src_dir, old_name)
            if not os.path.exists(dest):
                print(f"-> Переносим {old_name} из корня в src/...")
                shutil.move(root_file, dest)
            else:
                print(f"-> Удаляем дубликат {old_name} из корня...")
                os.remove(root_file)

    # Переносим также main_app.py из корня в src/, если он там залежался
    root_main = os.path.join(script_dir, "main_app.py")
    if os.path.exists(root_main):
        dest_main = os.path.join(src_dir, "main_app.py")
        if not os.path.exists(dest_main):
            print("-> Переносим main_app.py из корня в src/...")
            shutil.move(root_main, dest_main)
        else:
            print("-> Удаляем дубликат main_app.py из корня...")
            os.remove(root_main)

    # 2. Переименовываем файлы внутри src/ в уникальные имена jh_*
    for old_name, new_name in rename_map.items():
        old_path = os.path.join(src_dir, old_name)
        new_path = os.path.join(src_dir, new_name)
        if os.path.exists(old_path):
            if os.path.exists(new_path):
                print(f"-> Найдена старая копия {old_name}. Удаляем её, так как jh_ версия уже существует.")
                os.remove(old_path)
            else:
                print(f"-> Уникализируем имя: {old_name} -> {new_name}")
                os.rename(old_path, new_path)

    # 3. Автоматически правим импорты во всех файлах внутри src/
    print("[Рефакторинг] Автоматическое обновление импортов и вызовов функций в кодовой базе...")
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()

                    # Правим импорты и обращения к модулям
                    modified = False
                    
                    # Заменяем storage_manager
                    if "storage_manager" in code and "jh_storage_manager" not in code:
                        code = code.replace("import storage_manager", "import jh_storage_manager")
                        code = code.replace("storage_manager.", "jh_storage_manager.")
                        modified = True
                        
                    # Заменяем ai_engine
                    if "ai_engine" in code and "jh_ai_engine" not in code:
                        code = code.replace("import ai_engine", "import jh_ai_engine")
                        code = code.replace("ai_engine.", "jh_ai_engine.")
                        modified = True
                        
                    # Заменяем results_ui
                    if "results_ui" in code and "jh_results_ui" not in code:
                        code = code.replace("import results_ui", "import jh_results_ui")
                        code = code.replace("results_ui.", "jh_results_ui.")
                        modified = True

                    if modified:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(code)
                        print(f"   ✓ Успешно обновлены импорты в файле: {file}")
                except Exception as e:
                    print(f"   [Ошибка рефакторинга] Не удалось обновить {file}: {e}")

def install_and_compile():
    # Автоматическое определение папки, где физически находится этот скрипт build_exe.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Принудительно меняем рабочую директорию процесса на папку проекта
    os.chdir(script_dir)
    print(f"[0/4] Рабочая директория сборщика установлена на: {script_dir}")

    # Запускаем автоматический рефакторинг перед сборкой
    run_self_healing_refactor(script_dir)

    print("\n[1/4] Проверка и установка необходимых утилит для сборки...")
    # Гарантируем, что PyInstaller установлен
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "customtkinter", "flask", "flask_cors", "pillow"], check=True)

    print("\n[2/4] Определение путей CustomTkinter...")
    try:
        import customtkinter
        ctk_path = os.path.dirname(customtkinter.__file__)
        ctk_data_arg = f"{ctk_path}{os.path.pathsep}customtkinter"
    except ImportError:
        print("[Ошибка]: Не удалось импортировать customtkinter для сборки.")
        return

    # Точка входа в структурированной папке src/
    main_script = os.path.join("src", "main_app.py")
    icon_file = "icon.ico"
    logo_file = "logo.png"

    if not os.path.exists(main_script):
        print(f"[Ошибка]: Главный файл {main_script} не найден в директории проекта ({script_dir})!")
        return

    print("\n[3/4] Запуск компиляции через PyInstaller...")
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",               # Не спрашивать подтверждение на перезапись
        "--onedir",                  # Собираем в одну папку
        "--windowed",                # Отключает появление консольного черного окна при запуске
        f"--add-data={ctk_data_arg}", # Вшиваем ассеты customtkinter
        "--paths=src",               # Указываем PyInstaller искать локальные импорты в папке src/
    ]

    if os.path.exists(icon_file):
        cmd.append(f"--icon={icon_file}")
        cmd.append(f"--add-data={icon_file}{os.path.pathsep}.")
    else:
        print("[Предупреждение]: Файл icon.ico не найден в корне. Сборка будет выполнена со стандартной иконкой.")

    if os.path.exists(logo_file):
        cmd.append(f"--add-data={logo_file}{os.path.pathsep}.")
    else:
        print("[Предупреждение]: Файл logo.png не найден в корне.")

    # Добавляем целевой скрипт в сборку
    cmd.append(main_script)

    print(f"Выполняется команда: {' '.join(cmd)}\n")
    
    # Запускаем сборку с захватом вывода, чтобы в случае ошибки детально распечатать traceback
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("\n==================================================")
        print("❌ СБОЙ ВЫПОЛНЕНИЯ PYINSTALLER!")
        print("==================================================")
        print("STDOUT (Стандартный вывод):")
        print(result.stdout)
        print("\nSTDERR (Поток ошибок):")
        print(result.stderr)
        print("==================================================")
        return

    # Пути к результатам сборки
    dist_app_dir = os.path.join(script_dir, "dist", "main_app")
    src_exe = os.path.join(dist_app_dir, "main_app.exe")
    src_internal = os.path.join(dist_app_dir, "_internal")

    # Находим целевую папку сборки инсталлятора
    parent_dir = os.path.dirname(script_dir)
    target_dir = os.path.join(parent_dir, "Job Hunter AI")
    
    if not os.path.exists(target_dir):
        target_dir = script_dir

    print(f"\n[4/4] Автоматический перенос файлов в целевую папку: {target_dir}...")
    
    try:
        # 1. Переносим и переименовываем EXE в "Job Hunter AI.exe"
        dest_exe = os.path.join(target_dir, "Job Hunter AI.exe")
        if os.path.exists(dest_exe):
            os.remove(dest_exe)
        shutil.move(src_exe, dest_exe)
        print("-> Файл Job Hunter AI.exe успешно перенесен и переименован.")

        # 2. Переносим папку зависимостей _internal
        dest_internal = os.path.join(target_dir, "_internal")
        if os.path.exists(dest_internal):
            shutil.rmtree(dest_internal)
        shutil.move(src_internal, dest_internal)
        print("-> Системная папка _internal успешно перенесена.")

        print("\n[Очистка]: Удаление временных папок сборки...")
        shutil.rmtree(os.path.join(script_dir, "build"))
        shutil.rmtree(os.path.join(script_dir, "dist"))
        spec_file = os.path.join(script_dir, "main_app.spec")
        if os.path.exists(spec_file):
            os.remove(spec_file)
        
        print("\n==================================================")
        print(" СБОРКА И АВТОПЕРЕНОС УСПЕШНО ЗАВЕРШЕНЫ!")
        print(f" Все файлы подготовлены в папке: {target_dir}")
        print("==================================================")

    except Exception as err:
        print(f"\n[Ошибка автопереноса/очистки]: {err}")

if __name__ == "__main__":
    install_and_compile()