#!/usr/bin/env python3
import json
import logging
import os
import subprocess
import sys
import time
import redis
from concurrent.futures import ThreadPoolExecutor

import ccxt
import requests
from dotenv import load_dotenv

# Добавляем путь к TA Engine
sys.path.append(os.path.join(os.getcwd(), "skills/indicators/scripts"))
try:
    import ta_engine
except ImportError:
    ta_engine = None

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

# Инициализация Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    REDIS_AVAILABLE = True
except Exception:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available. Falling back to JSON.")

def send_telegram(message):
    """Отправка уведомления в Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "your_chat_id":
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception:
        pass

def get_current_balance():
    """Получение баланса (Live с OKX или Paper из Redis/JSON)."""
    mode = os.getenv("TRADING_MODE", "PAPER")
    
    if mode == "PAPER":
        if REDIS_AVAILABLE:
            balance = r.get("trader:paper:balance")
            if balance:
                return float(balance)
        
        # Fallback to JSON
        if os.path.exists(PAPER_STATE_FILE):
            try:
                with open(PAPER_STATE_FILE) as f:
                    state = json.load(f)
                    val = state.get("balance", 100.0)
                    if REDIS_AVAILABLE:
                        r.set("trader:paper:balance", val)
                    return val
            except Exception:
                return 100.0
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
                       capture_output=True, text=True, check=False)
    except Exception as e:
        logging.error(f"Position sync failed: {e}")

def run_analysis(symbol, exchange):
    """Запуск TA Engine для конкретной пары (внутри процесса)."""
    if ta_engine is None:
        logging.error("TA Engine module not found!")
        return None
        
    try:
        # Прямой вызов функций из модуля ta_engine вместо subprocess.run
        df = ta_engine.fetch_data(symbol, "1h", limit=300, exchange=exchange)
        analysis = ta_engine.analyze(df)
        analysis["symbol"] = symbol
        return analysis
    except Exception as e:
        logging.error(f"In-process analysis failed for {symbol}: {e}")
        return None

def trigger_agent(analysis_data, avg_volatility):
    """Триггер ИИ-команды с учетом контекста портфеля."""
    symbol = analysis_data['symbol']
    rsi = analysis_data['data']['indicators']['rsi']
    trend = analysis_data['data']['signals']['trend']
    price = analysis_data['data']['price']
    
    # Чтение портфеля
    portfolio_ctx = "Balance: 100.0, Positions: None"
    if REDIS_AVAILABLE:
        bal = r.get("trader:paper:balance") or "100.0"
        pos_count = r.get("trader:paper:pos_count") or "0"
        pos_details = r.get("trader:paper:pos_symbols") or "None"
        portfolio_ctx = f"Balance: ${float(bal):.2f}, Positions Open: {pos_count} ({pos_details})"
    elif os.path.exists(PAPER_STATE_FILE):
        try:
            with open(PAPER_STATE_FILE) as f:
                state = json.load(f)
                bal = state.get('balance', 100.0)
                pos_count = len(state.get('positions', []))
                pos_details = ", ".join([p['symbol'] for p in state.get('positions', [])])
                portfolio_ctx = f"Balance: ${bal:.2f}, Positions Open: {pos_count} ({pos_details})"
        except Exception:
            pass

    # Динамический SL/TP на основе ATR (средний истинный диапазон)
    atr = data["indicators"].get("atr", 0)
    price = data["price"]
    
    # Рекомендуемый SL = 1.5 * ATR, TP = 3.0 * ATR (соотношение 1:2)
    sl_val = round(atr * 1.5, 4)
    tp_val = round(atr * 3.0, 4)
    
    prompt = f"""
    MARKET SIGNAL FOUND: {symbol}
    Current Price: {price}
    Trend: {data['signals']['trend']}
    RSI: {data['indicators']['rsi']}
    Volatility Index: {avg_volatility:.2f}%
    
    DYNAMIC RISK MANAGEMENT:
    - Stop-Loss: {sl_val} (~{ (sl_val/price)*100:.2f }%)
    - Take-Profit: {tp_val} (~{ (tp_val/price)*100:.2f }%)
    
    TASK: Analyze this setup and execute trade if it fits our strategy.
    """
    # Резервный метод через CLI если REST API недоступен или изменился
    try:
        logging.info(f"Triggering AI agent via CLI for {symbol}...")
        # Используем команду openclaw напрямую
        cmd = ["openclaw", "agent", "--agent", "lead", "--message", prompt, "--deliver"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
        
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
        start_time = time.time()
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
        
        # 3. Сканирование рынка (ПАРАЛЛЕЛЬНО + IN-PROCESS + REUSE CCXT)
        best_signal = None
        best_score = 0
        scanner_data = [] # Массив для Heatmap на дашборде
        volatility_sum = 0
        valid_coins = 0
        
        # Глобальный объект биржи для повторного использования (SSL reuse)
        static_exchange = ccxt.okx({'enableRateLimit': True})
        
        def process_symbol(symbol, exch=static_exchange):
            logging.info(f"Scanning {symbol}...")
            return symbol, run_analysis(symbol, exch)

        with ThreadPoolExecutor(max_workers=len(WATCHLIST)) as executor:
            results = list(executor.map(process_symbol, WATCHLIST))

        for symbol, analysis in results:
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
                if rsi < 32:
                    score = (32 - rsi) * 2 # Перепроданность (Long)
                elif rsi > 68:
                    score = (rsi - 68) * 2 # Перекупленность (Short)
                
                if score > best_score:
                    best_score = score
                    best_signal = analysis

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
        except Exception:
            pass

        # Auto-Killswitch (защита от Flash Crash)
        if avg_volatility > 5.0: # Если в среднем монеты гуляют более чем на 5% за свечу
            msg = f"⚠️ AUTO-KILLSWITCH: High Market Volatility ({avg_volatility:.2f}%). Execution paused."
            logging.warning(msg)
            # 4. Обработка сигналов (НЕБЛОКИРУЮЩАЯ)
        if best_signal and best_score > 10:
            logging.info(f"Signal found for {best_signal['symbol']} (Score: {best_score})")
            # Запускаем агента в отдельном потоке, чтобы не блокировать цикл
            executor.submit(trigger_agent, best_signal, avg_volatility)
        else:
            logging.info("No strong signals found in watchlist.")
            
        logging.info(f"Cycle completed in {time.time() - start_time:.2f}s. Sleeping...")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
