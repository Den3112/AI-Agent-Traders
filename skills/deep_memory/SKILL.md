---
name: deep_memory
description: Long-term persistent memory using Supabase.
---

# Deep Memory Skill

Этот навык позволяет агентам сохранять важную информацию, которая будет доступна даже после перезагрузки системы.

## Как использовать

### Запомнить информацию
```bash
python3 skills/deep_memory/scripts/deep_memory.py remember --agent "lead" --key "user_preferences" --value '{"lang": "ru", "mode": "aggresive"}'
```

### Вспомнить информацию
```bash
python3 skills/deep_memory/scripts/deep_memory.py recall --agent "lead" --key "user_preferences"
```

## Хранилище
- **Supabase**: Таблица `agent_memory`.
- **Redis**: Используется для кэширования (в разработке).
