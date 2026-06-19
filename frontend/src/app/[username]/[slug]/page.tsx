"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { getAvailableSlots, createBooking, listEventTypes } from "@/lib/api";
import { EventType, Slot } from "@/lib/types";

export default function BookingPage() {
  const params = useParams();
  const username = params.username as string;
  const slug = params.slug as string;

  const [eventType, setEventType] = useState<EventType | null>(null);
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [slots, setSlots] = useState<Slot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [form, setForm] = useState({
    name: "",
    email: "",
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  });

  const loadEventType = useCallback(async () => {
    try {
      const eventTypes = await listEventTypes();
      const found = eventTypes.find((et) => et.slug === slug);
      if (found) {
        setEventType(found);
      } else {
        setError("Event type not found");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, [slug]);

  const loadSlots = useCallback(async () => {
    if (!eventType) return;

    setSlotsLoading(true);
    try {
      const data = await getAvailableSlots(username, slug, selectedDate);
      setSlots(data.slots);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load slots");
    } finally {
      setSlotsLoading(false);
    }
  }, [username, slug, selectedDate, eventType]);

  useEffect(() => {
    loadEventType();
  }, [loadEventType]);

  useEffect(() => {
    if (eventType) {
      loadSlots();
    }
  }, [eventType, loadSlots]);

  async function handleBooking(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedSlot || !eventType) return;

    try {
      await createBooking(username, slug, {
        start: selectedSlot,
        attendee: {
          name: form.name,
          email: form.email,
          timeZone: form.timeZone,
        },
      });
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to book");
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error && !eventType) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Event Not Found
          </h1>
          <p className="text-gray-500">{error}</p>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Booked!</h1>
          <p className="text-gray-500">
            Your meeting has been scheduled. Check your email for confirmation.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {eventType?.title}
          </h1>
          <p className="text-gray-500 mb-4">
            {eventType?.length} minutes
            {eventType?.description && ` - ${eventType.description}`}
          </p>
          <p className="text-sm text-gray-400">
            Hosted by {username}
          </p>
        </div>

        {!success && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Select a Date & Time
            </h2>

            <div className="mb-6">
              <label htmlFor="booking-date" className="block text-sm font-medium text-gray-700 mb-2">
                Pick a date
              </label>
              <input
                id="booking-date"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                min={new Date().toISOString().split("T")[0]}
                className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {slotsLoading && (
              <div className="text-center py-8 text-gray-500">
                Loading available times...
              </div>
            )}

            {!slotsLoading && slots.length === 0 && (
              <div className="text-center py-8">
                <p className="text-gray-500">
                  No available times for this date
                </p>
              </div>
            )}

            {!slotsLoading && slots.length > 0 && (
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Available times
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {slots.map((slot) => {
                    const time = new Date(slot.time);
                    const timeStr = time.toLocaleTimeString("en-US", {
                      hour: "2-digit",
                      minute: "2-digit",
                      hour12: false,
                    });
                    return (
                      <button
                        key={slot.time}
                        onClick={() => setSelectedSlot(slot.time)}
                        className={`py-2 px-3 rounded-md text-sm font-medium ${
                          selectedSlot === slot.time
                            ? "bg-blue-600 text-white"
                            : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                        }`}
                      >
                        {timeStr}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {selectedSlot && (
              <form onSubmit={handleBooking} className="space-y-4 pt-4 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  Enter your details
                </h3>

                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Name *
                  </label>
                  <input
                    id="name"
                    type="text"
                    required
                    value={form.name}
                    onChange={(e) =>
                      setForm({ ...form, name: e.target.value })
                    }
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email *
                  </label>
                  <input
                    id="email"
                    type="email"
                    required
                    value={form.email}
                    onChange={(e) =>
                      setForm({ ...form, email: e.target.value })
                    }
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label htmlFor="timeZone" className="block text-sm font-medium text-gray-700">
                    Timezone
                  </label>
                  <input
                    id="timeZone"
                    type="text"
                    value={form.timeZone}
                    onChange={(e) =>
                      setForm({ ...form, timeZone: e.target.value })
                    }
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700"
                >
                  Confirm Booking
                </button>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
