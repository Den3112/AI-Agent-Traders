#!/usr/bin/env python3
"""
Скрипт для автоматической проверки целостности системы AI Trade Team.
Используется AI-агентами для верификации окружения перед работой.
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict

# Цвета для вывода в терминал
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_file(path: str) -> bool:
    if os.path.exists(path):
        print(f"{GREEN}✓{RESET} Файл найден: {path}")
        return True
    else:
        print(f"{RED}✗{RESET} Файл не найден: {path}")
        return False

def check_dir(path: str) -> bool:
    if os.path.isdir(path):
        print(f"{GREEN}✓{RESET} Директория найдена: {path}")
        return True
    else:
        print(f"{RED}✗{RESET} Директория не найдена: {path}")
        return False

def validate_openclaw_config(config_path: str):
    if not check_file(config_path):
        return
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        agents_config = config.get("agents", {})
        agents_list = agents_config.get("list", [])
        
        print(f"{GREEN}✓{RESET} Конфигурация OpenClaw валидна. Найдено агентов: {len(agents_list)}")
        
        for agent in agents_list:
            name = agent.get("name")
            id_ = agent.get("id")
            print(f"  - Агент: {name} (ID: {id_})")
            
    except Exception as e:
        print(f"{RED}✗{RESET} Ошибка при чтении openclaw.json: {e}")

def main():
    print(f"\n{YELLOW}=== Валидация системы AI Trade Team ==={RESET}\n")
    
    base_path = Path(__file__).parent.parent.parent
    
    # 1. Проверка структуры
    required_dirs = ["agents", "dashboard", "skills", "scripts"]
    for d in required_dirs:
        check_dir(str(base_path / d))
        
    # 2. Проверка критических файлов
    required_files = [".cursorrules", ".ai-instructions.md", "openclaw.json", ".env.example"]
    for f in required_files:
        check_file(str(base_path / f))
        
    # 3. Валидация конфига агентов
    validate_openclaw_config(str(base_path / "openclaw.json"))
    
    print(f"\n{YELLOW}=== Проверка завершена ==={RESET}\n")

if __name__ == "__main__":
    main()
