---
name: risk_mgmt
description: Advanced risk management for small balances and OKX exchange.
---

# Risk Management Skill

Этот навык обеспечивает выживаемость торгового счета. Он блокирует любые сделки, которые не соответствуют математическим лимитам безопасности.

## Как использовать

### Проверить сделку на безопасность
```bash
python3 skills/risk_mgmt/scripts/safe_entry.py --balance 100 --entry 75000 --stop 74000
```

## Правила «Золотого стандарта» для $100:
1. **Max Risk**: 1.5% от депозита.
2. **Min Order**: Ордера менее $10 отклоняются или корректируются (если риск позволяет).
3. **Hard Stop**: Сделки без стоп-лосса запрещены.
