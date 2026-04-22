# System Architecture: AI Trade Team

This document describes the high-level architecture and communication protocols of the AI Trading Team.

## 1. Multi-Agent Orchestration

The system follows a **Hierarchical Delegation Pattern**. Each agent is specialized for a specific domain, reducing the cognitive load on individual models and improving accuracy.

### Agent Flow

1. **Lead (Coordinator)**: Receives user requests via the Terminal channel. Analyzes the intent and breaks it down into sub-tasks.
2. **Analyst (Researcher)**: Digs into market data. Calls the `Data Aggregator` to fetch CEX/DEX prices and sentiments.
3. **Strategy Engineer (Quantitative)**: Receives analysis and applies mathematical models or backtesting logic.
4. **Portfolio Manager (Gatekeeper)**: Performs risk checks (`risk_mgmt`) and approves sizes.
5. **Execution (Operator)**: Interacts with Exchange APIs for final order placement.

## 2. Skill Infrastructure

Skills are modular units of capability. We categorize them into two types:

### A. Prompt-Based Skills
These skills use the LLM's inherent reasoning capabilities for non-deterministic tasks (e.g., news sentiment analysis).

### B. Hardened Tools (Python)

Critical tasks that require absolute precision are offloaded to Python scripts.

- **Location**: `/skills/{skill_name}/scripts/`
- **Execution**: The agent calls these scripts via the shell, receiving structured JSON output.

## 3. Communication Channels

- **Terminal**: Primary interface for the user.
- **Telegram**: Secondary event-based channel for notifications and alerts.
- **WebSocket**: Global event bus for agent-to-agent synchronization.

## 4. Security & Isolation

- **Шифрование**: Секреты управляются через `.env` и никогда не логируются.
- **Paper Trading**: Система по умолчанию использует имитационный уровень исполнения, если не установлена и не проверена переменная `TRADING_MODE=LIVE`.
- **Блокировки**: Управление сессиями предотвращает одновременное повреждение состояния с помощью файловых блокировок.

## 5. Схемы взаимодействия (JSON)

Для минимизации ошибок при разработке навыков (Skills), используйте следующие схемы.

### Схема ответа навыка (Skill Output)
```json
{
  "status": "success | error",
  "data": {
    "result": "Объект с данными",
    "metrics": {
      "execution_time": "float",
      "tokens_used": "int (optional)"
    }
  },
  "error": "Сообщение об ошибке (null если успех)"
}
```

### Схема риска (Risk Check)
```json
{
  "agent_id": "string",
  "action": "BUY | SELL",
  "symbol": "string",
  "amount": "float",
  "leverage": "int"
}
```

---

*Последнее обновление: 2026-04-19*
