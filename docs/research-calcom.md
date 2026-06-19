# Исследование cal.com — функциональность и базовый путь пользователя

## Что такое cal.com

cal.com — open-source платформа планирования встреч (аналог Calendly). Оригинальный стек: Next.js + React + tRPC + Prisma + PostgreSQL, видео через Daily.co. Мы изучали кодовую базу (Prisma-схему и README) для понимания реальной архитектуры и данных. Наш сервис строится на Python (Django/FastAPI), поэтому переносим логику и модель данных, а не код.

## Базовый путь пользователя — 3 шага

### Шаг 1. Создание типа встречи (EventType)

Тип встречи — это шаблон того, что можно забронировать. Каждый тип имеет:

| Поле | Описание | Пример |
|------|----------|--------|
| `title` | Название | «Консультация 1:1» |
| `slug` | URL-идентификатор | `consult` (итого: `/username/consult`) |
| `description` | Описание для гостя | «30-минутная встреча...» |
| `length` | Длительность в минутах | `30` |
| `locations` | Где пройдёт | Cal Video / Zoom / телефон / произвольная ссылка |
| `slotInterval` | Шаг сетки слотов (мин.) | `15` (слоты: 10:00, 10:15, 10:30...) |
| `minimumBookingNotice` | Мин. время до встречи (мин.) | `120` (нельзя бронировать менее чем за 2 ч) |
| `beforeEventBuffer` | Буфер перед встречей (мин.) | `5` (автоблок перед) |
| `afterEventBuffer` | Буфер после встречи (мин.) | `5` (автоблок после) |
| `requiresConfirmation` | Нужно ли подтверждение хоста | `false` |
| `seatsPerTimeSlot` | Макс. гостей в слоте (групповые) | `null` (1:1) |
| `periodType` | На какой горизонт доступно | `UNLIMITED` / `ROLLING` / `RANGE` |
| `bookingLimits` | Лимиты по интервалам | `{\"PER_DAY\": 3}` |
| `durationLimits` | Ограничения длительности | `{\"PER_WEEK\": 120}` |
| `bookingFields` | Поля формы для гостя | JSON (имя, email, доп. вопросы) |

После создания типу встречи привязывается **расписание** (Schedule + Availability), определяющее, когда хост доступен.

### Шаг 2. Доступность и страница бронирования

#### Доступность

- **Schedule** — именованное расписание (например, «Основное»), привязанное к пользователю. Содержит набор **Availability** — слоёв доступности:
  - `days` — дни недели `[0,1,2,3,4]` (пн-пт);
  - `startTime` / `endTime` — рабочие часы (`09:00` — `17:00`);
  - `date` — точечная дата (для исключений/праздников).
- Расписание может быть как на уровне пользователя (общее), так и на уровне типа встречи (персональное).

#### Вычисление свободных слотов

Свободные слоты **не хранятся в базе** — они вычисляются на лету:

```
1. Берём рабочие часы из Availability для выбранной даты
2. Разбиваем на слоты с шагом slotInterval
3. Вычитаем пересечения с существующими Booking (startTime..endTime + буферы)
4. Отсекаем слоты, которые наступят раньше чем minimumBookingNotice
5. Конвертируем результат в таймзону гостя
```

#### Страница бронирования

Публичный URL: `{BASE_URL}/{username}/{event-slug}`. Показывает:
- Название и описание типа встречи;
- Выбор даты (календарь);
- Список свободных слотов на выбранную дату (в таймзоне гостя);
- Форму с полями из `bookingFields` (имя, email, вопросы).

Для приватных ссылок есть механизм `HashedLink` (одноразовые/с лимитом).

### Шаг 3. Запись на свободный слот (Booking)

Гость выбирает слот и заполняет форму. Создаётся бронь:

| Поле | Описание |
|------|----------|
| `uid` | Публичный ID брони (для управления) |
| `eventTypeId` | Тип встречи |
| `startTime` / `endTime` | Начало и конец |
| `status` | `ACCEPTED` / `PENDING` / `CANCELLED` / `REJECTED` |
| `Attendee[]` | Гости: имя, email, таймзона |
| `responses` | Ответы на поля формы |
| `location` | Место проведения |

Далее в оригинальном cal.com: письма-уведомления, запись в календарь, создание видеоссылки, вебхуки. В нашем MVP это не требуется.

#### Жизненный цикл брони

```
Создание → (подтверждение хостом) → Проведение → Завершение
    ↓
Отмена / Перенос / No-show
```

## Минимальная модель данных под Python (Django ORM)

```python
# models.py — MVP

from django.db import models


class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    time_zone = models.CharField(max_length=64, default="Europe/London")

    def __str__(self):
        return self.username


class EventType(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_types")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    length = models.PositiveIntegerField(help_text="Длительность в минутах")
    slot_interval = models.PositiveIntegerField(default=15, help_text="Шаг сетки в минутах")
    minimum_booking_notice = models.PositiveIntegerField(default=120, help_text="Мин. время до встречи (мин.)")
    before_event_buffer = models.PositiveIntegerField(default=0, help_text="Буфер перед (мин.)")
    after_event_buffer = models.PositiveIntegerField(default=0, help_text="Буфер после (мин.)")
    requires_confirmation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("owner", "slug")]

    def __str__(self):
        return f"{self.owner.username}/{self.slug}"


class Schedule(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    name = models.CharField(max_length=255)
    time_zone = models.CharField(max_length=64, default="Europe/London")

    def __str__(self):
        return f"{self.owner.username} — {self.name}"


class Availability(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="availability")
    event_type = models.ForeignKey(EventType, null=True, blank=True, on_delete=models.CASCADE,
                                   help_text="Ограничение для конкретного типа встречи")
    days = models.JSONField(help_text="Дни недели: [0=пн..6=вс]")
    start_time = models.TimeField()
    end_time = models.TimeField()
    specific_date = models.DateField(null=True, blank=True, help_text="Исключение на конкретную дату")

    def __str__(self):
        return f"{self.schedule} [{self.days}] {self.start_time}-{self.end_time}"


class Booking(models.Model):
    class Status(models.TextChoices):
        ACCEPTED = "accepted", "Принята"
        PENDING = "pending", "Ожидает подтверждения"
        CANCELLED = "cancelled", "Отменена"
        REJECTED = "rejected", "Отклонена"

    uid = models.CharField(max_length=32, unique=True)
    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACCEPTED)
    responses = models.JSONField(default=dict, blank=True)
    location = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking {self.uid}"


class Attendee(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="attendees")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    time_zone = models.CharField(max_length=64, default="Europe/London")
    phone_number = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"
```

## Алгоритм вычисления свободных слотов (псевдокод)

```python
from datetime import datetime, time, timedelta, date
from zoneinfo import ZoneInfo

def get_available_slots(event_type, target_date, booker_tz, host_user):
    """
    Возвращает список свободных слотов на target_date (date) в таймзоне гостя.
    """
    host_tz = ZoneInfo(host_user.time_zone)
    booker_tz = ZoneInfo(booker_tz)

    # 1. Найти расписание для типа встречи
    schedule = event_type.schedule or host_user.schedules.first()
    if not schedule:
        return []

    # 2. Получить окна доступности на нужный день недели
    weekday = target_date.weekday()  # 0=пн..6=вс
    windows = schedule.availability.filter(days__contains=weekday)

    # 3. Сформировать кандидатов (слоты) с шагом slot_interval
    slot_duration = timedelta(minutes=event_type.length)
    interval = timedelta(minutes=event_type.slot_interval)
    now = datetime.now(host_tz)
    min_notice = timedelta(minutes=event_type.minimum_booking_notice)
    min_bookable = now + min_notice

    candidates = []
    for window in windows:
        slot_start = datetime.combine(target_date, window.start_time, tzinfo=host_tz)
        slot_end = datetime.combine(target_date, window.end_time, tzinfo=host_tz)
        current = slot_start
        while current + slot_duration <= slot_end:
            if current >= min_bookable:
                candidates.append(current)
            current += interval

    # 4. Загрузить занятые слоты на дату (с учётом буферов)
    day_start = datetime.combine(target_date, time.min, tzinfo=host_tz)
    day_end = datetime.combine(target_date, time.max, tzinfo=host_tz)
    bookings = Booking.objects.filter(
        event_type=event_type,
        status__in=["accepted", "pending"],
        start_time__lt=day_end,
        end_time__gt=day_start,
    )
    booked_ranges = [
        (
            b.start_time - timedelta(minutes=event_type.before_event_buffer),
            b.end_time + timedelta(minutes=event_type.after_event_buffer),
        )
        for b in bookings
    ]

    # 5. Отфильтровать пересечения
    available = []
    for slot in candidates:
        slot_end = slot + slot_duration
        occupied = any(
            slot < booked_end and slot_end > booked_start
            for booked_start, booked_end in booked_ranges
        )
        if not occupied:
            # Конвертация в таймзону гостя
            slot_in_booker_tz = slot.astimezone(booker_tz)
            available.append(slot_in_booker_tz)

    return available
```

## Эскиз REST API

```
Создание типа встречи:
  POST   /api/v1/event-types          → создать тип встречи
  GET    /api/v1/event-types          → список типов встреч текущего пользователя
  GET    /api/v1/event-types/{id}     → получить тип встречи

Просмотр свободных слотов:
  GET    /api/v1/{username}/{slug}/slots?date=2026-06-16&timezone=Europe/Moscow
         → [{ "time": "2026-06-16T10:00:00+03:00", "available": true }, ...]

Запись на слот:
  POST   /api/v1/{username}/{slug}/bookings
         Body: { "start": "2026-06-16T10:00:00+03:00",
                 "attendee": { "name": "...", "email": "...", "timeZone": "..." },
                 "responses": {} }
         → { "uid": "abc123", "status": "accepted", ... }
```

## Вне рамок MVP (осознанно откладываем)

- Оплата и интеграция со Stripe;
- Видеозвонки (Cal Video, Zoom, Daily.co);
- Команды, роли, round-robin;
- Вебхуки и интеграции;
- Перенос и отмена брони;
- Уведомления по email/SMS;
- Групповые встречи (seatsPerTimeSlot);
- Рекуррентные встречи;
- Кастомные домены и SEO.
