#!/usr/bin/env python3
"""
market_data.py - Hardened Tool for fetching CEX prices.
Part of the AI Trade Team Golden Standard.
"""

import sys
import json
import requests
import argparse
from typing import Dict, Any

def get_binance_price(symbol: str) -> Dict[str, Any]:
    """Fetches real-time price from Binance Public API."""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper().replace('/', '')}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "symbol": symbol,
            "price": float(data['price']),
            "source": "Binance",
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "source": "Binance"}

def main():
    parser = argparse.ArgumentParser(description="Fetch real-time market data.")
    parser.add_argument("symbol", help="Ticker symbol (e.g., BTC/USDT)")
    args = parser.parse_args()

    # Standardize symbol for Binance (BTC/USDT -> BTCUSDT)
    result = get_binance_price(args.symbol)
    
    # Output structured JSON for the Agent to parse
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
