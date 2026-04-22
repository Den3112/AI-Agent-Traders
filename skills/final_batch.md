# SKILL: OrderBookAnalyzer
---
name: OrderBookAnalyzer
description: Анализ стакана (L2)
---
```python
def run(symbol):
    return {"bids_vs_asks": 1.2, "liquidity": "high", "spread": 0.01}
```

---
# SKILL: PortfolioTracker
---
name: PortfolioTracker
description: Мониторинг текущего баланса
---
```python
def run():
    return {"total_equity": 12500, "open_positions": 2, "daily_pnl": 150}
```

---
# SKILL: StrategyOptimizer
---
name: StrategyOptimizer
description: Оптимизация параметров стратегии
---
```python
def run(strategy_name):
    return {"optimized_ema": 21, "optimized_tp": 0.05}
```

---
# SKILL: LogicLogger
---
name: LogicLogger
description: Логирование решений в БД
---
```python
def run(event, agent):
    # Запись в SQLite
    return {"status": "logged"}
```

---
# SKILL: HumanApprovalWait
---
name: HumanApprovalWait
description: Ожидание подтверждения от человека
---
```python
def run(order_details):
    # В OpenClaw это вызывает интерактивное событие
    return {"status": "waiting_for_user", "priority": "CRITICAL"}
```
