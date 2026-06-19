"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listEventTypes } from "@/lib/api";
import { EventType } from "@/lib/types";

export default function Home() {
  const [eventTypes, setEventTypes] = useState<EventType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await listEventTypes();
        setEventTypes(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Event Types</h1>
        <Link
          href="/event-types/new"
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
        >
          Create Event Type
        </Link>
      </div>

      {loading && (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {!loading && !error && eventTypes.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No event types yet</p>
          <Link
            href="/event-types/new"
            className="text-blue-600 hover:text-blue-800"
          >
            Create your first event type
          </Link>
        </div>
      )}

      {!loading && !error && eventTypes.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {eventTypes.map((et) => (
            <div
              key={et.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                {et.title}
              </h2>
              <p className="text-sm text-gray-500 mb-4">
                /{et.owner_username}/{et.slug}
              </p>
              <div className="space-y-1 text-sm text-gray-600">
                <p>Duration: {et.length} min</p>
                <p>Slot interval: {et.slotInterval} min</p>
                {et.description && (
                  <p className="text-gray-500 mt-2 line-clamp-2">
                    {et.description}
                  </p>
                )}
              </div>
              <div className="mt-4 pt-4 border-t border-gray-100">
                <Link
                  href={`/${et.owner_username}/${et.slug}`}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  View booking page
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
