#!/usr/bin/env python3
"""
Скрипт мониторинга здоровья AI Trade Team.
Анализирует логи и выявляет критические ошибки.
"""

import os
from pathlib import Path

# Цвета
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def analyze_logs(log_path: str):
    if not os.path.exists(log_path):
        print(f"{RED}Файл логов не найден: {log_path}{RESET}")
        return

    with open(log_path) as f:
        lines = f.readlines()

    last_100 = lines[-100:] if len(lines) > 100 else lines

    def count_errors(line_list):
        rl = 0
        tg = 0
        for line in line_list:
            if "429" in line or "rate_limit" in line.lower():
                rl += 1
            if "telegram" in line.lower() and "404" in line:
                tg += 1
        return rl, tg

    total_rl, total_tg = count_errors(lines)
    recent_rl, recent_tg = count_errors(last_100)

    print(f"\n{BLUE}=== Отчет о состоянии системы ==={RESET}\n")

    # Проверка Rate Limits
    print(f"{BLUE}[Лимиты API]{RESET}")
    if recent_rl > 0:
        print(f"{RED}⚠ Свежие ошибки (429): {recent_rl}{RESET}")
    else:
        print(f"{GREEN}✓ Свежих ошибок лимитов нет.{RESET}")
    print(f"Всего за сессию: {total_rl}")

    # Проверка Telegram
    print(f"\n{BLUE}[Telegram]{RESET}")
    if recent_tg > 0:
        print(f"{RED}⚠ Свежие ошибки (404): {recent_tg}{RESET}")
        print(f"  {YELLOW}Рекомендация: Проверьте, перезапущен ли Gateway с новым токеном.{RESET}")
    else:
        print(f"{GREEN}✓ Telegram подключен и работает (свежих ошибок нет).{RESET}")
    print(f"Всего за сессию: {total_tg}")

    print(f"\n{BLUE}================================={RESET}\n")

if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.parent
    log_file = base_path / "gateway.log"
    analyze_logs(str(log_file))
