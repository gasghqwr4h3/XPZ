#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X-Piratez Tech Tree Viewer - Main Entry Point

Этот скрипт объединяет все модули и генерирует HTML-файл с визуализацией дерева технологий.
Запускайте его из папки с модом X-Piratez (где находится папка user/mods/Piratez/).

Использование:
    python main.py
    
Или из любой директории, указав путь к моду:
    python main.py --mod-path /path/to/Dioxine_XPiratez
"""

import sys
import os
import argparse

# Добавляем текущую директорию в path для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RUL_FILE, HTML_OUTPUT, START_TECH
from parser import load_all_data
from html_generator import generate_html_file


def check_files_exist():
    """Проверка существования необходимых файлов"""
    missing = []
    
    if not os.path.exists(RUL_FILE):
        missing.append(RUL_FILE)
    
    from config import LANG_FILES
    for lang_code, path in LANG_FILES.items():
        if not os.path.exists(path):
            missing.append(path)
    
    return missing


def main(mod_path=None):
    """
    Основная функция генерации viewer'а
    
    Args:
        mod_path: Путь к директории мода (опционально)
    """
    print("=" * 60)
    print("X-Piratez Tech Tree Viewer v35")
    print("=" * 60)
    
    # Если указан путь к моду, обновляем конфигурацию
    if mod_path:
        print(f"\nUsing custom mod path: {mod_path}")
        from config import BASE_DIR
        # Здесь можно было бы динамически обновить пути в config
        # Но для простоты предполагаем, что скрипт запускается из нужной директории
    
    # Проверка файлов
    print("\nChecking required files...")
    missing_files = check_files_exist()
    
    if missing_files:
        print("\n⚠ WARNING: Some files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nMake sure you're running this script from the X-Piratez mod folder.")
        print("Expected structure:")
        print("  your_mod_folder/")
        print("    └── user/mods/Piratez/")
        print("        ├── Ruleset/Piratez.rul")
        print("        └── Language/en-US.yml, ru.yml")
        
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    # Загрузка данных
    print("\nParsing ruleset and language files...")
    raw_data, game_langs_data = load_all_data()
    
    if not raw_data:
        print("\n❌ ERROR: Failed to parse ruleset file!")
        return False
    
    tech_count = len(raw_data)
    lang_count = len(game_langs_data)
    print(f"✓ Loaded {tech_count} technologies")
    print(f"✓ Loaded {lang_count} language variants")
    
    # Генерация HTML
    print(f"\nGenerating HTML viewer...")
    output_file = generate_html_file(raw_data, game_langs_data)
    
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"\n✅ SUCCESS!")
        print(f"Output file: {output_file}")
        print(f"File size: {file_size:.2f} MB")
        print(f"\nOpen {output_file} in your browser to view the tech tree.")
        return True
    else:
        print("\n❌ ERROR: Failed to create output file!")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate X-Piratez Tech Tree Viewer HTML file"
    )
    parser.add_argument(
        '--mod-path', 
        type=str, 
        help='Path to X-Piratez mod folder (optional, uses current dir by default)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run with test data (no files required)'
    )
    
    args = parser.parse_args()
    
    if args.test:
        print("Running in TEST mode with sample data...")
        from parser import load_all_data
        from html_generator import generate_html_file
        
        # Тестовые данные
        test_raw = {
            "STR_SCHOOLING_2": {"deps": ["STR_SCHOOLING_1"], "unlocks": ["STR_BASIC_LASER"]},
            "STR_SCHOOLING_1": {"deps": [], "unlocks": ["STR_SCHOOLING_2"]},
            "STR_BASIC_LASER": {"deps": ["STR_SCHOOLING_2"], "unlocks": ["STR_ADVANCED_LASER"]},
            "STR_ADVANCED_LASER": {"deps": ["STR_BASIC_LASER"], "unlocks": []}
        }
        test_langs = {
            "en-US": [
                {"STR_SCHOOLING_2": "Advanced Schooling", "STR_SCHOOLING_1": "Basic Schooling", 
                 "STR_BASIC_LASER": "Basic Laser", "STR_ADVANCED_LASER": "Advanced Laser"},
                {"STR_SCHOOLING_2": "Learn advanced skills.", "STR_SCHOOLING_1": "Learn basic skills."}
            ],
            "ru": [
                {"STR_SCHOOLING_2": "Продвинутое обучение", "STR_SCHOOLING_1": "Базовое обучение",
                 "STR_BASIC_LASER": "Базовый лазер", "STR_ADVANCED_LASER": "Продвинутый лазер"},
                {"STR_SCHOOLING_2": "Изучите продвинутые навыки.", "STR_SCHOOLING_1": "Изучите базовые навыки."}
            ]
        }
        
        generate_html_file(test_raw, test_langs, output_path="test_viewer.html", start_tech="STR_SCHOOLING_2")
        print("Test file created: test_viewer.html")
    else:
        success = main(mod_path=args.mod_path)
        sys.exit(0 if success else 1)
