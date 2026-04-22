#!/usr/bin/env python3
"""
deep_memory.py - Оживляет память агента с помощью Supabase и Redis.
"""

import argparse
import json
import os
from typing import Any

import requests


def get_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        # Пытаемся прочитать из .env если не загружено
        try:
            with open(".env") as f:
                for line in f:
                    if line.startswith(f"{key}="):
                        return line.strip().split("=", 1)[1]
        except Exception:
            pass
    return val

SUPABASE_URL = get_env("SUPABASE_URL")
SUPABASE_KEY = get_env("SUPABASE_SERVICE_ROLE_KEY") or get_env("SUPABASE_ANON_KEY")

def remember(agent_id: str, key: str, value: Any, metadata: dict | None = None):
    """Сохраняет данные в Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/agent_memory"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    payload = {
        "agent_id": agent_id,
        "key": key,
        "value": value,
        "metadata": metadata or {}
    }
    
    try:
        # Upsert logic (insert with ON CONFLICT)
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [201, 204, 200]:
            return {"status": "success", "message": f"Memory '{key}' saved for {agent_id}"}
        else:
            return {"status": "error", "message": response.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def recall(agent_id: str, key: str):
    """Загружает данные из Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/agent_memory?agent_id=eq.{agent_id}&key=eq.{key}&select=*"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {"status": "success", "data": data[0] if data else None}
        else:
            return {"status": "error", "message": response.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Deep Memory Manager for AI Agents")
    parser.add_argument("action", choices=["remember", "recall"])
    parser.add_argument("--agent", required=True, help="ID агента")
    parser.add_argument("--key", required=True, help="Ключ памяти")
    parser.add_argument("--value", help="Значение (для remember)")
    
    args = parser.parse_args()
    
    if args.action == "remember":
        if not args.value:
            print(json.dumps({"status": "error", "message": "Value is required for remember"}))
            return
        # Пытаемся распарсить JSON если это объект
        try:
            val = json.loads(args.value)
        except Exception:
            val = args.value
        print(json.dumps(remember(args.agent, args.key, val), indent=2))
    
    elif args.action == "recall":
        print(json.dumps(recall(args.agent, args.key), indent=2))

if __name__ == "__main__":
    main()
