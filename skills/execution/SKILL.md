---
name: execution
description: Executes trade orders on OKX or Paper Simulator.
---

# Execution Skill

Этот навык отвечает за "физическое" открытие сделок на бирже или в симуляторе.

## Как использовать

### Открыть сделку
Всегда передавайте точные параметры цены входа и стоп-лосса. Тейк-профит (1:2) рассчитывается автоматически.

```bash
python3 skills/execution/scripts/okx_executor.py --symbol BTC/USDT --side buy --amount 0.001 --entry 65000 --stop 64000
```

## Режимы (из .env):
- `PAPER`: Сделка запишется в `data/paper_state.json`. Баланс виртуальный ($100).
- `LIVE`: Сделка уйдет на реальную биржу OKX.

> [!WARNING]
> Никогда не запускайте исполнение без предварительного вызова `safe_entry` для проверки лимитов риска.
