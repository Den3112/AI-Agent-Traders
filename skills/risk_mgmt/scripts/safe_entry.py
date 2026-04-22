#!/usr/bin/env python3
import argparse
import json


def validate_trade(balance, risk_percent, entry_price, stop_loss, min_notional=10.0):
    """
    Validates if a trade is safe for a small balance ($100).
    Args:
        balance: Total USDT balance.
        risk_percent: Max % of balance to lose on SL hit.
        entry_price: Market or Limit price.
        stop_loss: Exit price if trade goes wrong.
        min_notional: Minimum order size in USDT (OKX standard is ~10 USDT).
    """
    if balance < 10:
        return {"status": "error", "reason": "Insufficient balance for trading (< $10)"}
        
    risk_amount = balance * (risk_percent / 100)
    price_risk = abs(entry_price - stop_loss)
    
    if price_risk == 0:
        return {"status": "error", "reason": "Stop Loss cannot be equal to Entry Price"}
        
    # Position size in units
    position_units = risk_amount / price_risk
    notional_value = position_units * entry_price
    
    # OKX / Exchange check
    if notional_value < min_notional:
        # If the risk-calculated size is too small, we might need to increase size to min_notional
        # BUT that increases the risk. So we must check if that increased risk is acceptable.
        adjusted_risk = (min_notional / entry_price) * price_risk
        adjusted_risk_percent = (adjusted_risk / balance) * 100
        
        if adjusted_risk_percent > 3.0: # Hard cap 3% for emergencies
             return {
                "status": "error", 
                "reason": f"Trade too small for exchange ($10 min), and increasing size would risk {round(adjusted_risk_percent, 2)}% of capital. Avoid this trade."
            }
        else:
            return {
                "status": "warning",
                "reason": "Position size adjusted to meet exchange minimum ($10).",
                "data": {
                    "original_notional": round(notional_value, 2),
                    "new_notional": min_notional,
                    "new_risk_percent": round(adjusted_risk_percent, 2),
                    "position_size": round(min_notional / entry_price, 6)
                }
            }

    return {
        "status": "success",
        "data": {
            "balance": balance,
            "risk_amount": round(risk_amount, 2),
            "position_size": round(position_units, 6),
            "notional_value": round(notional_value, 2),
            "risk_percent": risk_percent
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Institutional $100 Risk Engine")
    parser.add_argument("--balance", type=float, default=100.0)
    parser.add_argument("--risk", type=float, default=1.5)
    parser.add_argument("--entry", type=float, required=True)
    parser.add_argument("--stop", type=float, required=True)
    parser.add_argument("--min", type=float, default=10.0, help="Min notional (OKX default 10)")

    args = parser.parse_args()
    
    result = validate_trade(args.balance, args.risk, args.entry, args.stop, args.min)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
