#!/usr/bin/env python3
import json
import logging
import os
from datetime import datetime

import ccxt
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
load_dotenv()

STATE_FILE = "data/paper_state.json"
OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://localhost:18789/chat")

def load_paper_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        return json.load(f)

def save_paper_state(state):
    state["last_update"] = datetime.utcnow().isoformat() + "Z"
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_current_price(symbol):
    try:
        exchange = ccxt.okx()
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        logging.error(f"Failed to fetch price for {symbol}: {e}")
        return None

def trigger_performance_report(closed_position, result_pnl):
    """Уведомление Performance Analyst о закрытой сделке."""
    msg = f"""
[TRADE CLOSED]
ID: {closed_position['id']}
Symbol: {closed_position['symbol']}
Result: {'PROFIT' if result_pnl > 0 else 'LOSS'}
PnL: {result_pnl:.2f} USDT
Entry: {closed_position['entry_price']}
Exit: {closed_position['exit_price']}

Performance Analyst, проведи ретроспективу этой сделки и запиши выводы в Deep Memory.
"""
    payload = {"agentId": "lead", "sessionId": "auto", "message": msg}
    try:
        requests.post(OPENCLAW_URL, json=payload)
    except Exception:
        pass

def sync_paper_positions():
    state = load_paper_state()
    if not state or not state["positions"]:
        return

    active_positions = []
    pnl_changes = False

    for pos in state["positions"]:
        current_price = get_current_price(pos["symbol"])
        if current_price is None:
            active_positions.append(pos)
            continue

        hit_tp = (pos["side"] == "buy" and current_price >= pos["take_profit"]) or \
                 (pos["side"] == "sell" and current_price <= pos["take_profit"])
        
        hit_sl = (pos["side"] == "buy" and current_price <= pos["stop_loss"]) or \
                 (pos["side"] == "sell" and current_price >= pos["stop_loss"])

        if hit_tp or hit_sl:
            close_reason = "TP" if hit_tp else "SL"
            pos["exit_price"] = current_price
            pos["exit_time"] = datetime.utcnow().isoformat() + "Z"
            pos["reason"] = close_reason
            
            # Расчет прибыли/убытка
            if pos["side"] == "buy":
                pnl = (current_price - pos["entry_price"]) * pos["amount"]
            else:
                pnl = (pos["entry_price"] - current_price) * pos["amount"]
            
            pos["pnl"] = pnl
            state["balance"] += (pos["amount"] * pos["entry_price"]) + pnl
            state["history"].append(pos)
            
            logging.info(f"POSITION CLOSED ({close_reason}): {pos['symbol']} PnL: {pnl:.2f}")
            trigger_performance_report(pos, pnl)
            pnl_changes = True
        else:
            active_positions.append(pos)

    if pnl_changes:
        state["positions"] = active_positions
        save_paper_state(state)

def main():
    logging.info("Syncing paper positions...")
    sync_paper_positions()

if __name__ == "__main__":
    main()
