#!/usr/bin/env python3
import os
import json
import argparse
import ccxt
import logging
from datetime import datetime
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
load_dotenv()

STATE_FILE = "data/paper_state.json"

def load_paper_state():
    if not os.path.exists(STATE_FILE):
        return {"balance": 100.0, "positions": [], "history": []}
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_paper_state(state):
    state["last_update"] = datetime.utcnow().isoformat() + "Z"
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def execute_paper(symbol, side, amount, entry_price, stop_loss, take_profit_arg=None):
    state = load_paper_state()
    
    # Auto-size logic if amount <= 0
    if amount <= 0:
        import subprocess
        try:
            cmd = ["python3", "skills/execution/scripts/position_sizer.py", 
                   "--balance", str(state["balance"]), "--entry", str(entry_price), "--stop", str(stop_loss)]
            res = subprocess.run(cmd, capture_output=True, text=True)
            size_data = json.loads(res.stdout)
            amount = size_data["size"]
            logging.info(f"Auto-calculated position size: {amount} (Risk ~2%)")
        except Exception as e:
            logging.error(f"Failed to auto-calc size: {e}")
            return False

    if amount <= 0:
        logging.error("Final amount is zero or negative.")
        return False

    # Расчет Take Profit (Используем переданный или RR 1:2)
    if take_profit_arg:
        take_profit = take_profit_arg
    else:
        risk = abs(entry_price - stop_loss)
        take_profit = entry_price + (risk * 2) if side == "buy" else entry_price - (risk * 2)
    
    # Проверка баланса
    cost = amount * entry_price
    if state["balance"] < cost:
        logging.error(f"Insufficient paper balance: {state['balance']} < {cost}")
        return False

    position = {
        "id": f"paper_{int(datetime.timestamp(datetime.now()))}",
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    state["balance"] -= cost
    state["positions"].append(position)
    save_paper_state(state)
    
    logging.info(f"PAPER ORDER OPENED: {side} {amount} {symbol} at {entry_price}. TP: {take_profit}, SL: {stop_loss}")
    return True

def execute_live(symbol, side, amount, entry_price, stop_loss, take_profit_arg=None):
    try:
        # In live, auto-size would require fetching live balance
        if amount <= 0:
            logging.error("Auto-size in LIVE mode not yet fully supported (requires live balance mapping).")
            return False

        exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_API_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'enableRateLimit': True,
        })
        
        if take_profit_arg:
            tp_price = take_profit_arg
        else:
            tp_price = entry_price + (abs(entry_price - stop_loss) * 2) if side == "buy" else entry_price - (abs(entry_price - stop_loss) * 2)

        params = {
            'stopLoss': {
                'triggerPrice': stop_loss,
                'price': stop_loss * 0.99 if side == "buy" else stop_loss * 1.01 
            },
            'takeProfit': {
                'triggerPrice': tp_price
            }
        }
        
        order = exchange.create_order(symbol, 'market', side, amount, None, params)
        logging.info(f"LIVE ORDER PLACED: {order['id']}")
        return True
    except Exception as e:
        logging.error(f"LIVE ORDER FAILED: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Trade Executor for OKX/Paper")
    parser.add_argument("--symbol", required=True, help="BTC/USDT")
    parser.add_argument("--side", required=True, choices=["buy", "sell"])
    parser.add_argument("--amount", type=float, required=True, help="Amount (set 0 for auto-risk sizing)")
    parser.add_argument("--entry", type=float, required=True, help="Current entry price")
    parser.add_argument("--stop", type=float, required=True, help="Stop loss price")
    parser.add_argument("--tp", type=float, required=False, help="Take profit price (optional)")
    
    args = parser.parse_args()
    
    mode = os.getenv("TRADING_MODE", "PAPER")
    
    if mode == "PAPER":
        success = execute_paper(args.symbol, args.side, args.amount, args.entry, args.stop, args.tp)
    else:
        success = execute_live(args.symbol, args.side, args.amount, args.entry, args.stop, args.tp)
        
    if success:
        print(json.dumps({"status": "success", "message": "Order executed"}))
    else:
        print(json.dumps({"status": "error", "message": "Execution failed"}))

if __name__ == "__main__":
    main()
