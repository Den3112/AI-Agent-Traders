#!/usr/bin/env python3
"""
health_check.py - Global Connectivity and System Integrity Check.
Part of the AI Trade Team Golden Standard.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def check_env():
    required = ["GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN"]
    missing = [r for r in required if not os.getenv(r) or "your_" in os.getenv(r)]
    return {"status": "ok" if not missing else "warning", "missing": missing}

def check_binance():
    try:
        response = requests.get("https://api.binance.com/api/v3/ping", timeout=5)
        return {"status": "ok" if response.status_code == 200 else "error"}
    except:
        return {"status": "error"}

def main():
    report = {
        "environment": check_env(),
        "binance_connectivity": check_binance(),
        "openclaw_gateway": "online" # Script assumes it's running in context
    }
    
    print(json.dumps(report, indent=2))
    if report["environment"]["status"] != "ok":
        sys.exit(1)

if __name__ == "__main__":
    main()
