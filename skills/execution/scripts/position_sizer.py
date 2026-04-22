#!/usr/bin/env python3
import argparse
import json


def calculate_position_size(balance, entry_price, stop_loss, risk_percent=2.0):
    """
    Рассчитывает размер позиции так, чтобы при срабатывании Stop Loss 
    убыток составил не более `risk_percent` от `balance`.
    """
    if balance <= 0 or entry_price <= 0 or stop_loss <= 0:
        return 0.0

    risk_amount = balance * (risk_percent / 100.0)
    stop_distance_per_unit = abs(entry_price - stop_loss)

    if stop_distance_per_unit == 0:
        return 0.0 # Защита от деления на ноль

    # Сколько единиц актива мы можем купить, чтобы суммарный убыток = risk_amount
    position_size = risk_amount / stop_distance_per_unit
    
    # Защита от чрезмерного плеча: если позиция больше баланса (без плеча)
    # мы пока ограничиваем покупку стоимостью 100% баланса
    max_position_size_no_leverage = balance / entry_price
    position_size = min(position_size, max_position_size_no_leverage)

    return round(position_size, 6)

def main():
    parser = argparse.ArgumentParser(description="Position Sizer (Kelly / Fixed Risk)")
    parser.add_argument("--balance", type=float, required=True, help="Current Portfolio Balance (USDT)")
    parser.add_argument("--entry", type=float, required=True, help="Entry Price")
    parser.add_argument("--stop", type=float, required=True, help="Stop Loss Price")
    parser.add_argument("--risk", type=float, default=2.0, help="Risk percent per trade (default: 2.0%)")

    args = parser.parse_args()

    size = calculate_position_size(args.balance, args.entry, args.stop, args.risk)
    
    cost = size * args.entry
    risk_usd = abs(args.entry - args.stop) * size

    print(json.dumps({
        "status": "success",
        "size": size,
        "cost_usdt": round(cost, 2),
        "projected_loss_usdt": round(risk_usd, 2)
    }))

if __name__ == "__main__":
    main()
