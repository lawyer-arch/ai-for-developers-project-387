import { getAuthHeaders, logout } from "./auth";
import {
  EventType,
  CreateEventType,
  Schedule,
  CreateSchedule,
  Availability,
  CreateAvailability,
  SlotsResponse,
  Booking,
  CreateBooking,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

const PUBLIC_PATHS = ["/slots", "/bookings"];

function isPublic(path: string): boolean {
  return PUBLIC_PATHS.some((p) => path.includes(p));
}

async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (!isPublic(path)) {
    Object.assign(headers, getAuthHeaders());
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...headers,
      ...options?.headers,
    },
  });

  if (response.status === 401 && typeof window !== "undefined") {
    logout();
    throw new Error("Session expired");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// Event Types
export async function listEventTypes(): Promise<EventType[]> {
  return fetchApi<EventType[]>("/api/v1/event-types");
}

export async function getEventType(id: number): Promise<EventType> {
  return fetchApi<EventType>(`/api/v1/event-types/${id}`);
}

export async function createEventType(
  data: CreateEventType
): Promise<EventType> {
  return fetchApi<EventType>("/api/v1/event-types", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// Schedules
export async function listSchedules(): Promise<Schedule[]> {
  return fetchApi<Schedule[]>("/api/v1/schedules");
}

export async function createSchedule(data: CreateSchedule): Promise<Schedule> {
  return fetchApi<Schedule>("/api/v1/schedules", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function addAvailability(
  scheduleId: number,
  data: CreateAvailability
): Promise<Availability> {
  return fetchApi<Availability>(
    `/api/v1/schedules/${scheduleId}/availability`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}

// Slots
export async function getAvailableSlots(
  username: string,
  slug: string,
  date: string,
  timezone: string = "Europe/Moscow"
): Promise<SlotsResponse> {
  const params = new URLSearchParams({ date, timezone });
  return fetchApi<SlotsResponse>(
    `/api/v1/${username}/${slug}/slots?${params.toString()}`
  );
}

// Bookings
export async function createBooking(
  username: string,
  slug: string,
  data: CreateBooking
): Promise<Booking> {
  return fetchApi<Booking>(`/api/v1/${username}/${slug}/bookings`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}
