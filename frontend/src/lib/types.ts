export interface User {
  id: number;
  username: string;
  email: string;
  name?: string;
  timeZone: string;
}

export interface EventType {
  id: number;
  title: string;
  slug: string;
  description?: string;
  length: number;
  slotInterval: number;
  minimumBookingNotice: number;
  beforeEventBuffer: number;
  afterEventBuffer: number;
  requiresConfirmation: boolean;
  location?: string;
  scheduleId?: number;
  owner_id: number;
  owner_username: string;
  createdAt: string;
}

export interface CreateEventType {
  title: string;
  slug: string;
  description?: string;
  length: number;
  slotInterval?: number;
  minimumBookingNotice?: number;
  beforeEventBuffer?: number;
  afterEventBuffer?: number;
  requiresConfirmation?: boolean;
  location?: string;
  scheduleId?: number;
}

export interface Schedule {
  id: number;
  name: string;
  timeZone: string;
  availability: Availability[];
  owner_id: number;
}

export interface Availability {
  id: number;
  days: string;
  startTime: string;
  endTime: string;
  specificDate?: string;
}

export interface CreateSchedule {
  name: string;
  timeZone?: string;
}

export interface CreateAvailability {
  days: string;
  startTime: string;
  endTime: string;
  specificDate?: string;
}

export interface Slot {
  time: string;
  available: boolean;
}

export interface SlotsResponse {
  date: string;
  timezone: string;
  slots: Slot[];
}

export interface Attendee {
  name: string;
  email: string;
  timeZone: string;
  phoneNumber?: string;
}

export interface Booking {
  uid: string;
  eventTypeId: number;
  startTime: string;
  endTime: string;
  status: string;
  attendees: Attendee[];
  responses: Record<string, unknown>;
  location?: string;
  createdAt: string;
}

export interface CreateBooking {
  start: string;
  attendee: {
    name: string;
    email: string;
    timeZone: string;
    phoneNumber?: string;
  };
  responses?: Record<string, unknown>;
  location?: string;
}

export interface CreateAttendee {
  name: string;
  email: string;
  timeZone: string;
  phoneNumber?: string;
}
