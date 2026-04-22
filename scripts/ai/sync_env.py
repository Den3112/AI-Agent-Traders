#!/usr/bin/env python3
"""
Скрипт для синхронизации .env и .env.example.
Добавляет отсутствующие ключи в .env.example без их значений.
"""

import os
from pathlib import Path

def sync_env():
    base_path = Path(__file__).parent.parent.parent
    env_path = base_path / ".env"
    example_path = base_path / ".env.example"
    
    if not env_path.exists():
        print("Файл .env не найден.")
        return
        
    # Читаем ключи из .env
    with open(env_path, 'r') as f:
        env_lines = f.readlines()
        
    env_keys = []
    for line in env_lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            env_keys.append(line.split('=')[0])
            
    # Читаем ключи из .env.example
    example_keys = []
    if example_path.exists():
        with open(example_path, 'r') as f:
            example_lines = f.readlines()
        for line in example_lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                example_keys.append(line.split('=')[0])
    
    # Ищем недостающие ключи
    missing_keys = [k for k in env_keys if k not in example_keys]
    
    if not missing_keys:
        print("Файл .env.example уже синхронизирован.")
        return
        
    print(f"Добавление {len(missing_keys)} ключей в .env.example...")
    
    with open(example_path, 'a') as f:
        if not example_path.exists() or os.path.getsize(example_path) == 0:
            f.write("# Environment Variables Example\n")
        else:
            f.write("\n# Автоматически добавленные ключи AI-агентом\n")
            
        for key in missing_keys:
            f.write(f"{key}=\n")
            print(f"  + {key}")
            
    print("Готово.")

if __name__ == "__main__":
    sync_env()
