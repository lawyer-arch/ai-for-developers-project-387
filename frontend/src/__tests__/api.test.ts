import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  listEventTypes,
  getEventType,
  createEventType,
  listSchedules,
  createSchedule,
  addAvailability,
  getAvailableSlots,
  createBooking,
} from "@/lib/api";

const mockFetch = vi.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockClear();
});

describe("API Client", () => {
  describe("listEventTypes", () => {
    it("fetches event types list", async () => {
      const mockData = [
        {
          id: 1,
          title: "Consultation",
          slug: "consult",
          length: 30,
          slotInterval: 15,
          minimumBookingNotice: 120,
          beforeEventBuffer: 0,
          afterEventBuffer: 0,
          requiresConfirmation: false,
          owner_id: 1,
          owner_username: "demo",
          createdAt: "2026-01-01T00:00:00Z",
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await listEventTypes();
      expect(result).toEqual(mockData);
      expect(mockFetch).toHaveBeenCalledWith(
        "/api/v1/event-types",
        expect.objectContaining({
          headers: { "Content-Type": "application/json" },
        })
      );
    });

    it("throws on error response", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: "Internal server error" }),
      });

      await expect(listEventTypes()).rejects.toThrow("Internal server error");
    });
  });

  describe("createEventType", () => {
    it("creates event type with correct data", async () => {
      const newData = {
        title: "Meeting",
        slug: "meeting",
        length: 60,
      };

      const mockResponse = {
        id: 2,
        ...newData,
        slotInterval: 15,
        minimumBookingNotice: 120,
        beforeEventBuffer: 0,
        afterEventBuffer: 0,
        requiresConfirmation: false,
        owner_id: 1,
        owner_username: "demo",
        createdAt: "2026-01-01T00:00:00Z",
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await createEventType(newData);
      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        "/api/v1/event-types",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify(newData),
        })
      );
    });
  });

  describe("listSchedules", () => {
    it("fetches schedules list", async () => {
      const mockData = [
        {
          id: 1,
          name: "Working hours",
          timeZone: "Europe/Moscow",
          availability: [],
          owner_id: 1,
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await listSchedules();
      expect(result).toEqual(mockData);
    });
  });

  describe("getAvailableSlots", () => {
    it("fetches slots with correct params", async () => {
      const mockData = {
        date: "2026-06-15",
        timezone: "Europe/Moscow",
        slots: [
          { time: "2026-06-15T10:00:00+03:00", available: true },
          { time: "2026-06-15T10:30:00+03:00", available: true },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await getAvailableSlots(
        "testuser",
        "consult",
        "2026-06-15",
        "Europe/Moscow"
      );
      expect(result).toEqual(mockData);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/testuser/consult/slots?"),
        expect.anything()
      );
    });
  });

  describe("createBooking", () => {
    it("creates booking with correct data", async () => {
      const bookingData = {
        start: "2026-06-15T10:00:00+03:00",
        attendee: {
          name: "John Doe",
          email: "john@example.com",
          timeZone: "Europe/Moscow",
        },
      };

      const mockResponse = {
        uid: "abc123",
        eventTypeId: 1,
        startTime: "2026-06-15T10:00:00+03:00",
        endTime: "2026-06-15T10:30:00+03:00",
        status: "accepted",
        attendees: [bookingData.attendee],
        responses: {},
        createdAt: "2026-06-15T09:00:00Z",
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await createBooking("testuser", "consult", bookingData);
      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        "/api/v1/testuser/consult/bookings",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify(bookingData),
        })
      );
    });
  });
});
