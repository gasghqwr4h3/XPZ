# config.py
# Конфигурация путей и настроек для X-Piratez Tech Viewer

import os

# Базовая директория (можно менять при запуске из другого места)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Путь к основному файлу правил
# Относительный путь, как было в оригинале, или можно сделать абсолютным через BASE_DIR
RUL_FILE = os.path.join(BASE_DIR, 'user/mods/Piratez/Ruleset/Piratez.rul')

# Пути к языковым файлам
LANG_FILES = {
    'en-US': os.path.join(BASE_DIR, 'user/mods/Piratez/Language/en-US.yml'),
    'ru': os.path.join(BASE_DIR, 'user/mods/Piratez/Language/ru.yml')
}

# Выходной файл
HTML_OUTPUT = os.path.join(BASE_DIR, 'pirate_viewer_v35.html')

# Стартовая технология при запуске
START_TECH = "STR_SCHOOLING_2"

# Настройки графа по умолчанию
DEFAULT_DEPTH = 3
DEFAULT_HUB_LIMIT = 5
