#!/usr/bin/env python3
"""
risk_calculator.py - Position Sizing and VaR Calculator.
Part of the AI Trade Team Golden Standard.
"""

import argparse
import json
from typing import Any


def calculate_position(balance: float, risk_percent: float, entry_price: float, stop_loss: float) -> dict[str, Any]:
    """Calculates position size based on balance and risk per trade."""
    risk_amount = balance * (risk_percent / 100)
    price_risk = abs(entry_price - stop_loss)
    
    if price_risk == 0:
        return {"status": "error", "message": "Entry price cannot be equal to Stop Loss."}
    
    position_size = risk_amount / price_risk
    notional_value = position_size * entry_price
    
    return {
        "status": "success",
        "balance": balance,
        "risk_amount": risk_amount,
        "position_size_units": round(position_size, 6),
        "notional_value": round(notional_value, 2),
        "risk_reward_ratio": round(abs(entry_price - stop_loss) / entry_price, 4)
    }

def main():
    parser = argparse.ArgumentParser(description="Calculate trade risk and position size.")
    parser.add_argument("--balance", type=float, required=True, help="Total account balance")
    parser.add_argument("--risk", type=float, default=1.0, help="Risk percent per trade (default 1%)")
    parser.add_argument("--entry", type=float, required=True, help="Entry price")
    parser.add_argument("--stop", type=float, required=True, help="Stop loss price")
    
    args = parser.parse_args()

    result = calculate_position(args.balance, args.risk, args.entry, args.stop)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
