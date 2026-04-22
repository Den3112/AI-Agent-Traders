# AI Memory: История проекта AI Trade Team

Этот файл служит долгосрочной памятью для AI-агентов. Он обновляется после выполнения крупных задач.

## 📅 Последние события (2026-04-19)

### 🏗 Настройка окружения (Gold Standard)

- **Результат**: Созданы файлы `.cursorrules`, `.ai-instructions.md`, обновлены системные правила в `dashboard`.
- **Инструменты**: Добавлены скрипты `validate_system.py` и `sync_env.py`.
- **Архитектура**: В `ARCHITECTURE.md` добавлены JSON-схемы для навыков (Skills).

### 🔍 Исследование проблем (Текущее состояние)

- **Rate Limits (429)**: Добавлены дополнительные ключи Google и OpenRouter API. Теперь риск простоев минимален.
- **Telegram (404)**: Установлен реальный токен бота `@autodielyonline24_sk_bot`. Ожидается перезапуск Gateway для активации.
- **Интеграции**: Добавлены ключи Supabase, Redis (Upstash), Pinecone, xAI (Grok), Perplexity и Vercel. Система полностью укомплектована.

### 🛠 Новые инструменты

- **[AI_MEMORY.md](file:///home/creator/PROJECTS/AI_agent_traders/AI_MEMORY.md)**: Долгосрочная память проекта.
- **[scripts/ai/check_health.py](file:///home/creator/PROJECTS/AI_agent_traders/scripts/ai/check_health.py)**: Мониторинг лимитов и ошибок API.

## 🛠 Текущий статус агентов

- **Lead**: Готов, координирует работу.
- **Market Analyst**: Готов, имеет доступ к CCXT.
- **Strategy Engineer**: Готов.
- **Portfolio Manager**: Готов.
- **Execution Agent**: Готов.
- **Data Aggregator**: Готов.

## 📌 Важные решения

1. **Язык**: Основной язык разработки и общения — **Русский**.
2. **UI**: Только Vanilla CSS, премиальный дизайн (Glassmorphism).
3. **Безопасность**: Секреты хранятся строго в `.env`.

## 🚧 Известные баги и проблемы

1. Ошибки Telegram (404) из-за отсутствия валидного токена.
2. Лимиты API Gemini при интенсивной работе.
