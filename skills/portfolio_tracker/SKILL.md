---
name: portfolio_tracker
description: Tracks open positions, balances and trade history.
---

# Portfolio Tracker Skill

Этот навык позволяет ИИ видеть текущее состояние своего счета и открытых сделок.

## Как использовать

### Синхронизировать позиции
Скрипт проверяет все открытые ордера и закрывает их, если цена достигла Stop Loss или Take Profit.

```bash
python3 skills/portfolio_tracker/scripts/sync_positions.py
```

### Проверить баланс (Paper)
Чтение текущего состояния из базы данных симулятора.

```bash
cat data/paper_state.json
```

## Автоматизация
Синхронизация должна запускаться перед каждым циклом анализа рынка, чтобы ИИ понимал, свободен ли его капитал.
