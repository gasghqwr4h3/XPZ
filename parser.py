# parser.py
# Модуль парсинга данных из файлов мода X-Piratez

import os
import re
from config import RUL_FILE, LANG_FILES


def clean_ufo_text(text):
    """Очистка текста описания от служебных тегов"""
    if not text:
        return ""
    text = text.replace('{NEWLINE}', '\n').replace('\\n', '\n')
    text = re.sub(r'\{.*?\}', '', text)
    text = re.sub(r'<.*?>', '', text)
    return text.strip()


def parse_lang_file(filepath):
    """
    Парсинг языкового файла (.yml)
    Возвращает два словаря: lang (названия) и ufo (описания из UFOPEDIA)
    """
    lang, ufo = {}, {}
    if not os.path.exists(filepath):
        return lang, ufo
    
    try:
        with open(filepath, 'r', encoding='utf-8-sig', errors='replace') as f:
            content = f.read()
            # Ищем строки вида STR_XXX: "текст"
            matches = re.findall(r'^\s*(STR_[A-Z0-9_]+):\s*"(.*?)"', content, re.MULTILINE)
            for k, v in matches:
                if k.endswith('_UFOPEDIA'):
                    ufo[k.replace('_UFOPEDIA', '')] = clean_ufo_text(v)
                else:
                    lang[k] = v.replace('"', "'")
    except Exception as e:
        print(f"Warning: Error parsing {filepath}: {e}")
    
    return lang, ufo


def extract_tech_data(block_content):
    """
    Extract all technology data from a block: dependencies, unlocks, disables, cost, points
    """
    def get_list(key):
        pattern = rf'{key}:(.*?)(?=\n\s*[a-z]|$)'
        match = re.search(pattern, block_content, re.DOTALL)
        if match:
            return list(set(re.findall(r'(STR_[A-Z0-9_]+)', match.group(1))))
        return []
    
    def get_int(key, default=0):
        pattern = rf'{key}:\s*(-?\d+)'
        match = re.search(pattern, block_content)
        return int(match.group(1)) if match else default
    
    return {
        "deps": get_list("dependencies"),
        "unlocks": get_list("unlocks"),
        "disables": get_list("disables"),
        "cost": get_int("cost", 0),
        "points": get_int("points", 0)
    }


def parse_rul_file(filepath):
    """
    Parse the main rules file (.rul)
    Returns a dictionary of technologies with their full data
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        raw_data = {}
        # Find all technology blocks starting with "- name: STR_..."
        entries = re.finditer(
            r'^\s*-\s+name:\s*(STR_[A-Z0-9_]+)(.*?)(?=^\s*-\s+name:|\Z)',
            content,
            re.DOTALL | re.MULTILINE
        )
        
        for match in entries:
            tech_id = match.group(1)
            block = match.group(2)
            
            # Skip deleted entries
            if 'delete:' in block[:20]:
                continue
            
            raw_data[tech_id] = extract_tech_data(block)
        
        return raw_data
    
    except Exception as e:
        print(f"Error parsing RUL file: {e}")
        return None


def load_all_data():
    """
    Загрузка всех данных: парсинг RUL и языковых файлов
    Возвращает кортеж (raw_data, game_langs_data)
    """
    # Загрузка языковых данных
    all_game_data = {}
    for code, path in LANG_FILES.items():
        lang_dict, ufo_dict = parse_lang_file(path)
        if lang_dict or ufo_dict:
            all_game_data[code] = [lang_dict, ufo_dict]
    
    # Если языковые файлы не найдены, создаём пустую структуру
    if not all_game_data:
        all_game_data['en-US'] = [{}, {}]
        print("Warning: No language files found, using empty data")
    
    # Парсинг основного файла правил
    raw_data = parse_rul_file(RUL_FILE)
    
    return raw_data, all_game_data


if __name__ == "__main__":
    # Test the parser module
    print("Testing parser module...")
    raw, langs = load_all_data()
    if raw:
        print(f"Found {len(raw)} technologies")
        # Show first technology as example
        first_tech = next(iter(raw))
        print(f"\nExample: {first_tech}")
        print(f"  Dependencies: {raw[first_tech]['deps'][:5]}...")
        print(f"  Unlocks: {raw[first_tech]['unlocks'][:5]}...")
        print(f"  Cost: {raw[first_tech]['cost']}")
        print(f"  Points: {raw[first_tech]['points']}")
    else:
        print("Failed to load data")
