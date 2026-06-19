# Scheduling Service

[![Actions Status](https://github.com/lawyer-arch/ai-for-developers-project-386/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/lawyer-arch/ai-for-developers-project-386/actions)
[![CI](https://github.com/lawyer-arch/ai-for-developers-project-386/actions/workflows/ci.yml/badge.svg)](https://github.com/lawyer-arch/ai-for-developers-project-386/actions/workflows/ci.yml)

Сервис планирования встреч — аналог Cal.com. Пользователь создаёт типы встреч, расписания, а клиенты бронируют слоты через публичную страницу.

## Стек

| Компонент | Технологии |
|-----------|-----------|
| Контракт API | TypeSpec → OpenAPI 3.1 |
| Бэкенд | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic |
| БД | SQLite |
| Фронтенд | Next.js 16, TypeScript, Tailwind CSS |
| Тесты | pytest, vitest, Playwright |
| Инфраструктура | Docker Compose, Makefile |

## Быстрый старт

### Docker (рекомендуется)

```bash
docker compose up --build
```

- Фронтенд: http://localhost:3000
- Бэкенд (Swagger): http://localhost:8000/docs
- Демо-пользователь: `demo`, расписание: пн–пт 09:00–17:00, тип встречи: `consult`

Остановка:

```bash
docker compose down
```

### Локально (2 терминала)

```bash
# Терминал 1 — бэкенд
make dev

# Терминал 2 — фронтенд
make frontend-dev
```

Seed-данные (для сквозного сценария бронирования):

```bash
make seed
```

## Структура проекта

```
.
├── spec/                  # TypeSpec-спецификация → OpenAPI 3.1
├── backend/               # FastAPI-сервер
│   ├── app/api/           # Эндпоинты
│   ├── app/models/        # SQLAlchemy-модели
│   ├── app/schemas/       # Pydantic-схемы
│   └── app/seed.py        # Демо-данные
├── frontend/              # Next.js-приложение
│   └── src/app/           # Страницы (App Router)
├── tests/e2e/             # Playwright-тесты
├── docker-compose.yml
├── Makefile
└── package.json           # Корневой (Playwright)
```

## Команды Makefile

| Команда | Описание |
|---------|----------|
| `make install` | Установка зависимостей всех компонентов |
| `make compile-spec` | Компиляция TypeSpec в OpenAPI |
| `make migrate` | Применение миграций Alembic |
| `make seed` | Заполнение БД demo-данными |
| `make dev` | Запуск бэкенда (uvicorn --reload) |
| `make test` | Тесты бэкенда (pytest) |
| `make lint` | Линтер и типизация бэкенда (ruff + mypy) |
| `make frontend-install` | Установка зависимостей фронтенда |
| `make frontend-dev` | Запуск фронтенда (next dev) |
| `make frontend-build` | Сборка фронтенда |
| `make frontend-test` | Тесты фронтенда (vitest) |
| `make frontend-lint` | Линтер фронтенда (eslint) |
| `make e2e-install` | Установка Playwright и Chromium |
| `make e2e` | E2E-тесты (Playwright) |
| `make docker-build` | Сборка Docker-образов |
| `make docker-up` | Запуск в фоне |
| `make docker-down` | Остановка |
| `make docker-logs` | Логи |
| `make clean` | Удаление кеша и артефактов |

## Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `SCHEDULING_DATABASE_URL` | `sqlite+aiosqlite:///./scheduling.db` | URL подключения к БД |
| `SCHEDULING_JWT_SECRET` | `change-me-in-production` | Секрет для подписи JWT |
| `SCHEDULING_JWT_EXPIRE_MINUTES` | `1440` | Время жизни JWT (минуты) |
| `API_PROXY_TARGET` | `http://localhost:8000` | Цель прокси для Next.js rewrites |

## Тесты

| Набор | Команда | Кол-во | Что проверяется |
|-------|---------|--------|-----------------|
| Backend | `make test` | 3 | Health, создание и список event types |
| Frontend | `make frontend-test` | 11 | Рендер страниц, API-клиент |
| E2E | `make e2e` | 22 | Сценарии в реальном браузере |

### E2E-тесты (Playwright)

22 интеграционных теста в 5 группах:

**Homepage (3)** — список типов встреч, кнопки навигации.

**Booking page (10)** — выбор даты, загрузка слотов, форма бронирования, полный сценарий «дата → слот → заполнение → подтверждение», обработка ошибок.

**Create Event Type (3)** — рендер формы, создание типа встречи, отмена.

**Schedules (4)** — список расписаний, окна доступности, создание расписания, добавление availability.

**Navigation (2)** — проверка ссылок в header.

Запуск:

```bash
# Установка (один раз)
make e2e-install

# Запуск (приложение должно быть поднято)
make e2e
```

Отчёт:

```bash
npx playwright show-report
```

## CI/CD

### GitHub Actions

При каждом пуше в любую ветку автоматически:

1. Сборка и запуск Docker Compose (backend + frontend)
2. Ожидание готовности сервисов
3. Установка Playwright и Chromium
4. Запуск e2e-тестов
5. Загрузка отчёта при ошибках

### Release-please

При пуше в `main` автоматически создаётся/обновляется release-PR с changelog и предложением новой версии (semver). После мёржа release-PR создаётся GitHub Release.

Формат коммитов: [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `ci:` и др.).
