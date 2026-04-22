# SKILL: NewsSentimentScraper
---
name: NewsSentimentScraper
description: Анализ новостей и соцсетей
---
```python
def run(keyword="crypto"):
    return {"sentiment": "positive", "score": 0.85, "top_news": ["BTC reaches new ATH", "ETF inflows increase"]}
```

---
# SKILL: OnChainWhaleTracker
---
name: OnChainWhaleTracker
description: Отслеживание крупных транзакций
---
```python
def run(chain="eth"):
    return {"whale_activity": "high", "direction": "inflow_to_exchanges"}
```

---
# SKILL: MacroEconomicMonitor
---
name: MacroEconomicMonitor
description: Мониторинг макро-событий
---
```python
def run():
    return {"next_fed_meeting": "2026-05-01", "cpi_forecast": "unchanged"}
```

---
# SKILL: DEXPriceOracle
---
name: DEXPriceOracle
description: Цены с децентрализованных бирж
---
```python
def run(pair="SOL/USDC"):
    return {"dex": "Raydium", "price": 145.20}
```
