---
name: indicators
description: Provides technical indicators (RSI, EMA, ATR) for a given symbol on OKX.
---

# Technical Indicators Skill

Этот навык позволяет агентам получать точные математические данные о состоянии рынка. 

## Как использовать

### Получить анализ BTC/USDT на 1-часовом таймфрейме
```bash
python3 skills/indicators/scripts/ta_engine.py --symbol "BTC/USDT" --tf "1h"
```

## Выходные данные
Навык возвращает JSON с ценой, значениями индикаторов (RSI, EMA200, EMA50) и сигналами о тренде и волатильности.
