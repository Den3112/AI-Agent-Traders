#!/usr/bin/env python3
import argparse
import json

import ccxt
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def fetch_data(symbol, timeframe='1h', limit=100):
    """Fetch OHLCV from OKX."""
    exchange = ccxt.okx({
        'enableRateLimit': True,
    })
    
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        return f"Error fetching data: {str(e)}"

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=period).mean()

def analyze(df):
    """Calculate indicators and return signals."""
    if isinstance(df, str):
        return {"status": "error", "message": df}

    if len(df) < 200:
        return {"status": "error", "message": "Not enough data for processing (need at least 200 candles for EMA200)"}

    # Calculations
    df['RSI_14'] = calculate_rsi(df['close'], 14)
    df['EMA_200'] = calculate_ema(df['close'], 200)
    df['EMA_50'] = calculate_ema(df['close'], 50)
    df['ATR_14'] = calculate_atr(df, 14)
    
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    rsi = last_row['RSI_14']
    ema200 = last_row['EMA_200']
    ema50 = last_row['EMA_50']
    atr = last_row['ATR_14']
    current_price = last_row['close']
    
    # Logic
    trend = "bullish" if current_price > ema200 else "bearish"
    ema_cross = "golden_cross" if (last_row['EMA_50'] > last_row['EMA_200'] and prev_row['EMA_50'] <= prev_row['EMA_200']) else \
                "death_cross" if (last_row['EMA_50'] < last_row['EMA_200'] and prev_row['EMA_50'] >= prev_row['EMA_200']) else "none"
    
    avg_atr = df['ATR_14'].tail(50).mean()
    volatility = "high" if atr > (avg_atr * 1.5) else "low" if atr < (avg_atr * 0.7) else "normal"
    
    return {
        "status": "success",
        "timestamp": last_row['timestamp'].strftime('%Y-%m-%d %H:%M'),
        "symbol": "BTC/USDT", # default or derived
        "data": {
            "price": float(current_price),
            "indicators": {
                "rsi": float(round(rsi, 2)) if not pd.isna(rsi) else None,
                "ema200": float(round(ema200, 2)),
                "ema50": float(round(ema50, 2)),
                "atr": float(round(atr, 4)) if not pd.isna(atr) else None
            },
            "signals": {
                "trend": trend,
                "ema_cross": ema_cross,
                "volatility": volatility,
                "rsi_condition": "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
            }
        }
    }

def main():
    parser = argparse.ArgumentParser(description="OKX Technical Analysis Engine (Lite)")
    parser.add_argument("--symbol", type=str, default="BTC/USDT", help="Pair to analyze (default: BTC/USDT)")
    parser.add_argument("--tf", type=str, default="1h", help="Timeframe (1h, 4h, 1d)")
    
    args = parser.parse_args()
    
    df = fetch_data(args.symbol, args.tf, limit=300) # Increased limit for EMA stability
    analysis = analyze(df)
    analysis["symbol"] = args.symbol
    
    print(json.dumps(analysis, indent=2))

if __name__ == "__main__":
    main()
