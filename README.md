SQLAlchemy (+ драйвер для pgsql - asyncpg) - ОРМ
Alembic - Управление миграциями

Repository и Unit of Work - паттерны проектирования

Pytest (стандарт для Python) и HTTPX для асинхронных запросов к API - Тестирование

## Миграции (Alembic)

Все команды выполняются из корня проекта. Строка подключения к БД берётся из переменной окружения `DATABASE_URL`
(по умолчанию `postgresql+asyncpg://postgres:1234@localhost/wallets`, см. `src/database.py`).

### Создать новую миграцию

После изменения моделей в `src/models.py` сгенерируйте миграцию автоматически:

```bash
uv run alembic revision --autogenerate -m "описание изменений"
```

Файл миграции появится в `migrations/versions/`. **Обязательно проверьте его перед применением** —
autogenerate не всегда корректно определяет переименования столбцов/таблиц и некоторые изменения типов.

Пустая миграция (для ручного написания):

```bash
uv run alembic revision -m "описание изменений"
```

### Применить миграции

```bash
uv run alembic upgrade head      # до последней версии
uv run alembic upgrade +1        # на одну миграцию вперёд
```

### Откатить миграции

```bash
uv run alembic downgrade -1      # на одну миграцию назад
uv run alembic downgrade base    # откатить все миграции
```

### Полезные команды

```bash
uv run alembic current           # текущая версия БД
uv run alembic history           # список миграций
uv run alembic upgrade head --sql  # показать SQL без применения
```
