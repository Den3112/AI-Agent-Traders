import subprocess

tokens = [
    # Add tokens here for local testing only. DO NOT COMMIT TO GIT.
    # "ghp_...",
]


for t in tokens:
    print(f"Проверка {t[:10]}...", end=" ")
    cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
           "-H", f"Authorization: token {t}", "https://api.github.com/user"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.stdout.strip() == "200":
        print("✅ РАБОТАЕТ")
    else:
        print(f"❌ Ошибка {res.stdout.strip()}")
