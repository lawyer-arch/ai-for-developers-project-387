import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;
using OpenAPI;

@service
@server("http://localhost:8000")
namespace SchedulingApi;

// ──────────────────────────────────────────────
// Models
// ──────────────────────────────────────────────

model User {
  id: int32;
  username: string;
  email: string;
  name?: string;
  timeZone: string;
}

model EventType {
  id: int32;
  title: string;
  slug: string;
  description?: string;
  length: int32;
  slotInterval: int32;
  minimumBookingNotice: int32;
  beforeEventBuffer: int32;
  afterEventBuffer: int32;
  requiresConfirmation: boolean;
  location?: string;
  scheduleId?: int32;
  createdAt: utcDateTime;
}

model Schedule {
  id: int32;
  name: string;
  timeZone: string;
  availability: Availability[];
}

model Availability {
  id: int32;
  days: int32[];
  startTime: string;
  endTime: string;
  specificDate?: string;
}

model Slot {
  time: utcDateTime;
  available: boolean;
}

model SlotsResponse {
  date: string;
  timezone: string;
  slots: Slot[];
}

model Booking {
  uid: string;
  eventTypeId: int32;
  startTime: utcDateTime;
  endTime: utcDateTime;
  status: BookingStatus;
  attendees: Attendee[];
  responses: Record<unknown>;
  location?: string;
  createdAt: utcDateTime;
}

enum BookingStatus {
  accepted: "accepted",
  pending: "pending",
  cancelled: "cancelled",
  rejected: "rejected",
}

model Attendee {
  name: string;
  email: string;
  timeZone: string;
  phoneNumber?: string;
}

// ── Request ──

model CreateEventType {
  title: string;
  slug: string;
  description?: string;
  length: int32;
  slotInterval: int32 = 15;
  minimumBookingNotice: int32 = 120;
  beforeEventBuffer: int32 = 0;
  afterEventBuffer: int32 = 0;
  requiresConfirmation: boolean = false;
  location?: string;
  scheduleId?: int32;
}

model CreateSchedule {
  name: string;
  timeZone: string = "Europe/Moscow";
}

model CreateAvailability {
  days: int32[];
  startTime: string;
  endTime: string;
  specificDate?: string;
}

model CreateBooking {
  start: utcDateTime;
  attendee: CreateAttendee;
  responses?: Record<unknown>;
  location?: string;
}

model CreateAttendee {
  name: string;
  email: string;
  timeZone: string;
  phoneNumber?: string;
}

// ──────────────────────────────────────────────
// Routes
// ──────────────────────────────────────────────

@route("/api/v1/event-types")
@doc("Создание и список типов встреч")
namespace EventTypes {
  @doc("Создать тип встречи")
  @post
  op createEventType(@body body: CreateEventType): EventType;

  @doc("Список типов встреч текущего пользователя")
  @get
  op listEventTypes(): EventType[];
}

@route("/api/v1/event-types/{eventTypeId}")
@doc("Получение типа встречи по ID")
namespace EventTypeById {
  @doc("Получить тип встречи")
  @get
  op getEventType(@path eventTypeId: int32): EventType;
}

@route("/api/v1/schedules")
@doc("Управление расписаниями")
namespace Schedules {
  @doc("Создать расписание")
  @post
  op createSchedule(@body body: CreateSchedule): Schedule;

  @doc("Список расписаний текущего пользователя")
  @get
  op listSchedules(): Schedule[];
}

@route("/api/v1/schedules/{scheduleId}/availability")
@doc("Добавление окон доступности")
namespace ScheduleAvailability {
  @doc("Добавить окно доступности в расписание")
  @post
  op addAvailability(
    @path scheduleId: int32,
    @body body: CreateAvailability,
  ): Availability;
}

@route("/api/v1/{username}/{slug}/slots")
@doc("Просмотр свободных слотов")
namespace Slots {
  @doc("Свободные слоты на дату в таймзоне гостя")
  @get
  op getAvailableSlots(
    @path username: string,
    @path slug: string,
    @query date: string,
    @query timezone: string = "Europe/Moscow",
  ): SlotsResponse;
}

@route("/api/v1/{username}/{slug}/bookings")
@doc("Запись на встречу")
namespace Bookings {
  @doc("Записаться на свободный слот")
  @post
  op createBooking(
    @path username: string,
    @path slug: string,
    @body body: CreateBooking,
  ): Booking;
}
