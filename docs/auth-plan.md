# План внедрения аутентификации

## 1. Текущее состояние

| Компонент | Статус |
|---|---|
| **JWT config** | Есть в `config.py` (секрет, алгоритм, expire) |
| **Зависимости** | `pyjwt`, `passlib[bcrypt]` добавлены |
| **Модель User** | Нет поля `hashed_password` |
| **Модуль `auth/`** | Пустой `__init__.py` |
| **Middleware/Depend** | Нет |
| **`owner_id` в роутерах** | Хардкод `owner_id=1` с `# TODO: get from auth` |
| **Фронтенд `api.ts`** | Нет заголовков `Authorization` |
| **Фронтенд: страницы** | Нет логина/регистрации |
| **TypeSpec spec** | Нет security scheme, нет auth-эндпоинтов |
| **Slots/Bookings** | Публичные (верно — страница бронирования публична) |

## 2. Дорожная карта

### Этап 0: Спецификация API (TypeSpec)

Контракт — единый источник правды (Design First).

**Что сделать:**
- Добавить модель `AuthResponse` с полями `access_token`, `token_type`
- Добавить модели `LoginRequest` (username, password) и `RegisterRequest` (username, email, password, ...)
- Добавить эндпоинты:
  - `POST /api/v1/auth/register` — регистрация
  - `POST /api/v1/auth/login` — получение JWT
  - `GET /api/v1/auth/me` — текущий пользователь
- Добавить security scheme `BearerAuth` в TypeSpec
- Промаркировать защищённые эндпоинты `@useAuth(BearerAuth)`:
  - `POST/GET /api/v1/event-types`
  - `POST/GET /api/v1/schedules`
  - `POST /api/v1/schedules/{id}/availability`
- Оставить публичными (без auth):
  - `GET /api/v1/event-types/{id}`
  - `GET /api/v1/{username}/{slug}/slots`
  - `POST /api/v1/{username}/{slug}/bookings`
- Скомпилировать в OpenAPI: `make compile-spec`

### Этап 1: Модель данных

**Что сделать в `code/app/models/user.py`:**
- Добавить поле `hashed_password: Mapped[str] = mapped_column(String(255))`

**Pydantic схемы** (`code/app/schemas/auth.py`):
- `RegisterRequest` — username, email, password (с валидацией длины)
- `LoginRequest` — username, password
- `TokenResponse` — access_token, token_type
- `UserResponse` — существующие поля User

### Этап 2: Бэкенд — модуль аутентификации

**Файлы:**
- `code/app/auth/__init__.py` — экспорт функций
- `code/app/auth/jwt.py` — create_access_token, decode_access_token
- `code/app/auth/password.py` — hash_password, verify_password
- `code/app/auth/dependencies.py` — get_current_user (Depends)

**Ключевые решения:**
- JWT — синхронный HS256 (достаточно для одного хоста)
- `passlib.context.CryptContext(schemes=["bcrypt"])` для хешей
- `get_current_user` — FastAPI зависимость, читает `Authorization: Bearer <token>`, декодирует, получает пользователя из БД
- При ошибках — HTTPException 401

### Этап 3: Бэкенд — роутеры

**`code/app/api/auth.py`:**
- `POST /api/v1/auth/register` — создаёт пользователя, возвращает токен
- `POST /api/v1/auth/login` — проверяет пароль, возвращает токен
- `GET /api/v1/auth/me` — возвращает текущего пользователя (requires auth)

**Патч существующих роутеров:**
| Файл | Что сделать |
|---|---|
| `event_types.py` | Добавить `current_user: User = Depends(get_current_user)`, заменить `owner_id=1` на `owner_id=current_user.id` |
| `schedules.py` | Аналогично |
| `slots.py` | Не трогать — публичный |
| `bookings.py` | Не трогать — публичный |

**`code/app/main.py`:**
- Подключить `auth.router`

### Этап 4: Seed

**`code/app/seed.py`:**
- Добавить `hashed_password` в `SEED_USER`, например `"password123"`
- Использовать `hash_password()` из модуля auth

### Этап 5: Фронтенд

**`frontend/src/lib/types.ts`:**
- Добавить `LoginRequest`, `RegisterRequest`, `TokenResponse`, `UserResponse`

**`frontend/src/lib/auth.ts`:**
- Функции `login()`, `register()`, `logout()`, `getToken()`, `isAuthenticated()`
- Хранение токена в `localStorage` (ключ `scheduling_token`)
- `getAuthHeaders()` — возвращает `{ Authorization: "Bearer <token>" }`

**`frontend/src/lib/api.ts`:**
- В `fetchApi` добавить проброс `Authorization` из `getAuthHeaders()` (опционально)
- Исключить публичные эндпоинты (slots, bookings) из автоподстановки токена
- Добавить логику: при 401 → `logout()`, редирект на `/login`

**Страницы:**
- `frontend/src/app/auth/login/page.tsx` — форма логина
- `frontend/src/app/auth/register/page.tsx` — форма регистрации

**`frontend/src/app/layout.tsx`:**
- Если пользователь не аутентифицирован — показать ссылки Login/Register
- Если аутентифицирован — показать Logout, имя пользователя

**Защита маршрутов:**
- Страницы `/` (event-types), `/event-types/new`, `/schedules` — требуют аутентификации
- Если токена нет → редирект на `/auth/login`
- Публичные страницы: `/[username]/[slug]` (booking page), `/auth/login`, `/auth/register`

### Этап 6: Тесты

**Бэкенд:**
- `code/tests/test_auth.py`:
  - `test_register_success`
  - `test_register_duplicate_username`
  - `test_login_success`
  - `test_login_wrong_password`
  - `test_me_authenticated`
  - `test_me_unauthenticated`
- Обновить существующие тесты для event_types и schedules — добавить аутентификацию
- Использовать `factory_boy` для User с хешированным паролем

**Фронтенд:**
- Тесты для `auth.ts` (login, logout, getToken)
- Тесты для страниц логина/регистрации

### Этап 7: Удаление хардкода

После внедрения `get_current_user`:
- Убрать все `# TODO: get from auth`
- Убедиться, что `owner_id` нигде больше не хардкодится
- Проверить, что публичные эндпоинты (slots, bookings) не требуют токена

## 3. Проверка качества

На каждом этапе запускать:
```
make lint    # ruff + mypy
make test    # pytest
```

Финальная проверка:
- `make compile-spec` — спецификация компилируется
- `make lint` — нет ошибок ruff/mypy
- `make test` — все тесты проходят
- Ручная проверка e2e через `make e2e`

## 4. Итоговая архитектура

```
Клиент (браузер)                Сервер (FastAPI)
      │                              │
      │  POST /auth/login             │
      │  {username, password}         │
      ├─────────────────────────────► │  verify_password()
      │  {access_token, token_type}   │  create_access_token()
      │◄─────────────────────────────┤
      │                              │
      │  GET /api/v1/event-types      │
      │  Authorization: Bearer <jwt>  │
      ├─────────────────────────────► │  get_current_user()
      │  [EventType, ...]             │    → decode JWT
      │◄─────────────────────────────┤    → find User by id
      │                              │    → return User
      │                              │  filter by user.id
```

Публичные эндпоинты (slots, bookings) — без `Authorization`, роуты по username.
