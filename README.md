# Wallets REST API

![Python](https://img.shields.io/badge/Python_3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy_2-D71F00?logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

## Стек

| Категория | Технологии |
|---|---|
| Язык | Python 3.13, uv (окружение и зависимости) |
| Фреймворк | FastAPI, роутинг `/api/v1` |
| Валидация | Pydantic |
| База данных | PostgreSQL |
| ORM | SQLAlchemy 2 (async), asyncpg |
| Миграции | Alembic |
| Тесты | Pytest, pytest-asyncio, HTTPX |
| Деплой | Docker, Docker Compose |

## Как это работает

```text
Клиент ──JSON──▶ FastAPI ──▶ Pydantic (OperationRequest)   ← валидация входа
                    │
                    ▼  SessionDep (AsyncSession)
                SQLAlchemy (Wallet) ──SQL──▶ PostgreSQL ◀── Alembic (схема)
                    │
                    ▼
Клиент ◀──JSON── Pydantic (WalletResponse)                 ← сериализация выхода
```

- `src/main.py` — приложение, подключает роутер v1 с префиксом `/api/v1`
- `src/api/v1/` — эндпоинты и зависимости (сессия БД)
- `src/schemas/` — Pydantic-схемы, `src/models/` — SQLAlchemy-модели
- `src/database.py` — движок и сессии; строка подключения из `DATABASE_URL`
  (по умолчанию `postgresql+asyncpg://postgres:1234@localhost/wallets`)

## Эндпоинты

Базовый префикс: `/api/v1`. Интерактивная документация — `/docs`.

Объект кошелька (`WalletResponse`):

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "balance": "100.00",
  "created_at": "2026-10-15T12:00:00",
  "updated_at": "2026-10-15T12:00:00"
}
```

### `GET /api/v1/wallets`

Список всех кошельков.

- `200` — массив `WalletResponse`

### `POST /api/v1/wallets`

Создать кошелёк с нулевым балансом. Тело запроса не требуется.

- `200` — созданный `WalletResponse`

### `POST /api/v1/wallets/{wallet_uuid}/operation`

Пополнение или списание средств. Строка кошелька блокируется (`SELECT ... FOR UPDATE`),
поэтому параллельные операции над одним кошельком выполняются последовательно.

Тело запроса:

```json
{
  "operation_type": "DEPOSIT",
  "amount": 100.00
}
```

- `operation_type` — `DEPOSIT` или `WITHDRAW`
- `amount` — больше 0, до 10 цифр, не более 2 знаков после запятой

Ответы:

- `200` — обновлённый `WalletResponse`
- `400` — `Insufficient balance` (недостаточно средств для `WITHDRAW`)
- `404` — `Wallet not found`
- `422` — невалидное тело запроса или UUID

## Развёртывание на VPS (Docker Compose)

Поднимаются два контейнера: `db` (PostgreSQL 17, данные в volume `pgdata`, порт наружу не открыт)
и `api` (при старте применяет миграции `alembic upgrade head`, затем запускает uvicorn на порту 8000).

1. Установите Docker и плагин Compose (Ubuntu/Debian):

   ```bash
   curl -fsSL https://get.docker.com | sh
   ```

2. Склонируйте репозиторий и перейдите в него:

   ```bash
   git clone <url-репозитория> wallets-rest-api
   cd wallets-rest-api
   ```

3. Создайте `.env` из примера и задайте надёжный пароль БД:

   ```bash
   cp .env.example .env
   nano .env   # POSTGRES_PASSWORD, при необходимости API_PORT
   ```

4. Соберите и запустите:

   ```bash
   docker compose up -d --build
   ```

5. Проверьте:

   ```bash
   docker compose ps
   docker compose logs -f api
   curl http://localhost:8000/api/v1/wallets
   ```

   API доступно по `http://<ip-сервера>:8000/api/v1`, документация — `/docs`.
   Для продакшена лучше поставить перед API reverse-proxy с HTTPS (nginx, Caddy) и открыть наружу только 80/443.

Обновление после изменений в репозитории (миграции применятся автоматически):

```bash
git pull
docker compose up -d --build
```

Прочее:

```bash
docker compose down                                   # остановить (данные сохраняются)
docker compose down -v                                # остановить и удалить БД
docker compose exec api alembic current               # версия миграций в контейнере
docker compose exec db pg_dump -U postgres wallets > backup.sql  # бэкап БД
```

## Миграции (Alembic)

Команды выполняются из корня проекта, подключение берётся из `DATABASE_URL`.

```bash
uv run alembic revision --autogenerate -m "описание"  # новая миграция по моделям
uv run alembic revision -m "описание"                 # пустая миграция
uv run alembic upgrade head                           # применить все
uv run alembic downgrade -1                           # откатить одну
uv run alembic current                                # текущая версия БД
uv run alembic history                                # список миграций
uv run alembic upgrade head --sql                     # показать SQL без применения
```

Сгенерированные миграции (`migrations/versions/`) проверяйте перед применением: autogenerate
не всегда корректно распознаёт переименования и некоторые изменения типов.