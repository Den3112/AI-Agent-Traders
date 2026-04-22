#!/usr/bin/env python3
import json
import logging
import os
import subprocess
import time

import ccxt
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("heartbeat.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()

# Config
OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://localhost:18789/chat")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WATCHLIST = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]
INTERVAL = 1800 # 30 минут
BALANCE_LIMIT = 85.0 # Глобальный рубильник ($85)
PAPER_STATE_FILE = "data/paper_state.json"

def send_telegram(message):
    """Отправка уведомления в Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "your_chat_id":
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except:
        pass

def get_current_balance():
    """Получение баланса (Live с OKX или Paper из JSON)."""
    mode = os.getenv("TRADING_MODE", "PAPER")
    
    if mode == "PAPER":
        if os.path.exists(PAPER_STATE_FILE):
            with open(PAPER_STATE_FILE) as f:
                state = json.load(f)
                return state.get("balance", 100.0)
        return 100.0
    
    # LIVE Mode
    try:
        exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_API_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
        })
        balance = exchange.fetch_balance()
        return balance.get('USDT', {}).get('total', 0.0)
    except Exception as e:
        logging.error(f"Live balance check failed: {e}")
        return None

def sync_positions():
    """Запуск фонового мониторинга сделок."""
    try:
        subprocess.run(["python3", "skills/portfolio_tracker/scripts/sync_positions.py"], 
                       capture_output=True, text=True)
    except Exception as e:
        logging.error(f"Position sync failed: {e}")

def run_analysis(symbol):
    """Запуск TA Engine для конкретной пары."""
    try:
        cmd = ["python3", "skills/indicators/scripts/ta_engine.py", "--symbol", symbol]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return None
        analysis = json.loads(result.stdout)
        return analysis
    except Exception:
        return None

def trigger_agent(analysis_data, avg_volatility):
    """Триггер ИИ-команды с учетом контекста портфеля."""
    symbol = analysis_data['symbol']
    rsi = analysis_data['data']['indicators']['rsi']
    trend = analysis_data['data']['signals']['trend']
    price = analysis_data['data']['price']
    
    # Чтение портфеля
    portfolio_ctx = "Balance: 100.0, Positions: None"
    if os.path.exists(PAPER_STATE_FILE):
        try:
            with open(PAPER_STATE_FILE) as f:
                state = json.load(f)
                bal = state.get('balance', 100.0)
                pos_count = len(state.get('positions', []))
                pos_details = ", ".join([p['symbol'] for p in state.get('positions', [])])
                portfolio_ctx = f"Balance: ${bal:.2f}, Positions Open: {pos_count} ({pos_details})"
        except: pass

    prompt = f"[AUTONOMOUS SIGNAL] Signal for {symbol}: RSI={rsi}, Trend={trend}, Price: {price}. Market Volatility: {avg_volatility:.2f}%. Portfolio: {portfolio_ctx}. Analyze and execute risk-adjusted trade."
    
    # Резервный метод через CLI если REST API недоступен или изменился
    try:
        logging.info(f"Triggering AI agent via CLI for {symbol}...")
        # Используем команду openclaw напрямую
        cmd = ["openclaw", "agent", "--agent", "lead", "--message", prompt, "--deliver"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logging.info("AI agent triggered successfully via CLI.")
            send_telegram(f"🤖 ИИ проснулся! Лучший сигнал: {symbol} (RSI={rsi}). Портфель: {portfolio_ctx}.")
        else:
            logging.error(f"CLI trigger failed: {result.stderr}")
            # Пытаемся все же через REST как фоллбек (на случай если CLI сломан)
            response = requests.post(OPENCLAW_URL, json={"agentId": "lead", "message": prompt}, timeout=15)
            response.raise_for_status()
            
    except Exception as e:
        logging.error(f"Failed to trigger AI agent: {e}")
        send_telegram(f"⚠️ Ошибка вызова ИИ: {e}")


def main():
    mode = os.getenv("TRADING_MODE", "PAPER")
    logging.info(f"Starting MULTI-SCANNER HEARTBEAT ({mode}). Watchlist: {', '.join(WATCHLIST)}")
    send_telegram(f"🚀 Сканер рынка ({mode}) запущен! Список: {', '.join(WATCHLIST)}")
    
    while True:
        # Проверка глобальной паузы (Killswitch)
        if os.path.exists("data/pause.flag"):
            logging.info("Loop is PAUSED by Control Center.")
            time.sleep(10)
            continue
            
        # 1. Синхронизация текущих сделок (Watchdog)
        sync_positions()
        
        # 2. Проверка баланса (Circuit Breaker)
        balance = get_current_balance()
        if balance is not None:
            logging.info(f"Current Total Balance: ${balance:.2f}")
            if balance < BALANCE_LIMIT:
                msg = f"‼️ ALERT: CRITICAL BALANCE DROP (${balance:.2f}). TRADING STOPPED."
                logging.critical(msg)
                send_telegram(msg)
                break 
        
        # 3. Сканирование рынка
        best_signal = None
        best_score = 0
        scanner_data = [] # Массив для Heatmap на дашборде
        volatility_sum = 0
        valid_coins = 0
        
        for symbol in WATCHLIST:
            logging.info(f"Scanning {symbol}...")
            analysis = run_analysis(symbol)
            if analysis and analysis.get("status") == "success":
                data = analysis["data"]
                rsi = data["indicators"]["rsi"]
                price = data.get("price", 1)
                atr = data["indicators"].get("atr", 0)
                
                # Market Volatility (Абсолютный ATR к цене)
                atr_percent = (atr / price) * 100 if price > 0 else 0
                volatility_sum += atr_percent
                valid_coins += 1
                
                scanner_data.append({
                    "symbol": symbol,
                    "price": price,
                    "rsi": rsi,
                    "trend": data["signals"]["trend"],
                    "atr_percent": atr_percent
                })

                # Логика скоринга: ищем экстремальные значения RSI (<32 или >68)
                score = 0
                if rsi < 32: score = (32 - rsi) * 2 # Перепроданность (Long)
                elif rsi > 68: score = (rsi - 68) * 2 # Перекупленность (Short)
                
                if score > best_score:
                    best_score = score
                    best_signal = analysis
            
            time.sleep(1) # Защита от rate-limit

        # Индекс волатильности рынка
        avg_volatility = volatility_sum / valid_coins if valid_coins > 0 else 0

        # Сохраняем общий слепок рынка (+ волатильность)
        try:
            with open("data/market_state.json", "w") as f:
                json.dump({
                    "best_signal": best_signal,
                    "scanner": scanner_data,
                    "market_volatility": avg_volatility
                }, f)
        except: pass

        # Auto-Killswitch (защита от Flash Crash)
        if avg_volatility > 5.0: # Если в среднем монеты гуляют более чем на 5% за свечу
            msg = f"⚠️ AUTO-KILLSWITCH: High Market Volatility ({avg_volatility:.2f}%). Execution paused."
            logging.warning(msg)
            continue # Пропускаем вызов ИИ

        if best_signal and best_score > 0:
            logging.info(f"Best setup found: {best_signal['symbol']} (Score: {best_score:.2f})")
            trigger_agent(best_signal, avg_volatility)
        else:
            logging.info("No strong signals found in watchlist.")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
