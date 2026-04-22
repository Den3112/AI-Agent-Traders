import os
import subprocess
import json
from pathlib import Path

# Цвета
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def check_curl(name, url, headers=None, data=None, method="GET"):
    print(f"Проверка {BLUE}{name}{RESET}...", end=" ", flush=True)
    cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", method, url]
    if headers:
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
    if data:
        cmd.extend(["-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        status = result.stdout.strip()
        if status in ["200", "201", "204"]:
            print(f"{GREEN}ОК ({status}){RESET}")
            return True
        else:
            print(f"{RED}Ошибка ({status}){RESET}")
            return False
    except Exception as e:
        print(f"{RED}Ошибка: {e}{RESET}")
        return False

def check_redis(redis_url):
    print(f"Проверка {BLUE}Redis (Upstash){RESET}...", end=" ", flush=True)
    try:
        # Пытаемся подключиться через redis-cli если он есть
        cmd = ["redis-cli", "-u", redis_url, "ping"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if "PONG" in result.stdout:
            print(f"{GREEN}ОК (PONG){RESET}")
            return True
        else:
            print(f"{RED}Ошибка{RESET}")
            return False
    except:
        print(f"{YELLOW}redis-cli не найден, пропускаю...{RESET}")
        return None

def main():
    # Загружаем .env
    env_path = Path(".env")
    if not env_path.exists():
        print(f"{RED}.env не найден{RESET}")
        return

    env_vars = {}
    with open(env_path) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                env_vars[k] = v

    print(f"\n{BLUE}=== Верификация всех подключений ==={RESET}\n")

    # 1. Google Gemini
    check_curl("Gemini AI", 
               f"https://generativelanguage.googleapis.com/v1beta/models?key={env_vars.get('GOOGLE_API_KEY')}")

    # 2. Anthropic
    check_curl("Anthropic", 
               "https://api.anthropic.com/v1/messages", 
               method="POST",
               headers={
                   "x-api-key": env_vars.get("ANTHROPIC_API_KEY"),
                   "anthropic-version": "2023-06-01",
                   "Content-Type": "application/json"
               },
               data={"model": "claude-3-haiku-20240307", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]})

    # 3. OpenRouter
    check_curl("OpenRouter", 
               "https://openrouter.ai/api/v1/auth/key", 
               headers={"Authorization": f"Bearer {env_vars.get('OPENROUTER_API_KEY')}"})

    # 4. Perplexity
    check_curl("Perplexity", 
               "https://api.perplexity.ai/chat/completions",
               method="POST",
               headers={
                   "Authorization": f"Bearer {env_vars.get('PERPLEXITY_API_KEY')}",
                   "Content-Type": "application/json"
               },
               data={"model": "llama-3.1-8b-instruct", "messages": [{"role": "user", "content": "hi"}]})

    # 5. GitHub
    check_curl("GitHub (Current Token)", 
               "https://api.github.com/user", 
               headers={"Authorization": f"token {env_vars.get('GITHUB_TOKEN')}"})

    # 6. Supabase
    check_curl("Supabase API", 
               f"{env_vars.get('SUPABASE_URL')}/rest/v1/", 
               headers={
                   "apikey": env_vars.get("SUPABASE_ANON_KEY"),
                   "Authorization": f"Bearer {env_vars.get('SUPABASE_ANON_KEY')}"
               })

    # 7. Redis
    check_redis(env_vars.get("REDIS_URL"))

    print(f"\n{BLUE}==================================={RESET}\n")

if __name__ == "__main__":
    main()
