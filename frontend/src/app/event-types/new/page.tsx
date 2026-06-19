"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createEventType } from "@/lib/api";

export default function NewEventType() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    title: "",
    slug: "",
    description: "",
    length: 30,
    slotInterval: 15,
    minimumBookingNotice: 120,
    beforeEventBuffer: 0,
    afterEventBuffer: 0,
    requiresConfirmation: false,
    location: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await createEventType({
        ...form,
        description: form.description || undefined,
        location: form.location || undefined,
      });
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">
        Create Event Type
      </h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label
            htmlFor="title"
            className="block text-sm font-medium text-gray-700"
          >
            Title *
          </label>
          <input
            type="text"
            id="title"
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label
            htmlFor="slug"
            className="block text-sm font-medium text-gray-700"
          >
            Slug * (URL-friendly identifier)
          </label>
          <input
            type="text"
            id="slug"
            required
            pattern="[a-z0-9-]+"
            value={form.slug}
            onChange={(e) => setForm({ ...form, slug: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., consultation"
          />
        </div>

        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700"
          >
            Description
          </label>
          <textarea
            id="description"
            rows={3}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="length"
              className="block text-sm font-medium text-gray-700"
            >
              Duration (minutes) *
            </label>
            <input
              type="number"
              id="length"
              required
              min={1}
              value={form.length}
              onChange={(e) =>
                setForm({ ...form, length: parseInt(e.target.value) || 30 })
              }
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="slotInterval"
              className="block text-sm font-medium text-gray-700"
            >
              Slot Interval (minutes)
            </label>
            <input
              type="number"
              id="slotInterval"
              min={1}
              value={form.slotInterval}
              onChange={(e) =>
                setForm({
                  ...form,
                  slotInterval: parseInt(e.target.value) || 15,
                })
              }
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="minimumBookingNotice"
              className="block text-sm font-medium text-gray-700"
            >
              Minimum Notice (minutes)
            </label>
            <input
              type="number"
              id="minimumBookingNotice"
              min={0}
              value={form.minimumBookingNotice}
              onChange={(e) =>
                setForm({
                  ...form,
                  minimumBookingNotice: parseInt(e.target.value) || 120,
                })
              }
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="location"
              className="block text-sm font-medium text-gray-700"
            >
              Location
            </label>
            <input
              type="text"
              id="location"
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., Zoom, Google Meet"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="beforeEventBuffer"
              className="block text-sm font-medium text-gray-700"
            >
              Buffer Before (minutes)
            </label>
            <input
              type="number"
              id="beforeEventBuffer"
              min={0}
              value={form.beforeEventBuffer}
              onChange={(e) =>
                setForm({
                  ...form,
                  beforeEventBuffer: parseInt(e.target.value) || 0,
                })
              }
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="afterEventBuffer"
              className="block text-sm font-medium text-gray-700"
            >
              Buffer After (minutes)
            </label>
            <input
              type="number"
              id="afterEventBuffer"
              min={0}
              value={form.afterEventBuffer}
              onChange={(e) =>
                setForm({
                  ...form,
                  afterEventBuffer: parseInt(e.target.value) || 0,
                })
              }
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="requiresConfirmation"
            checked={form.requiresConfirmation}
            onChange={(e) =>
              setForm({ ...form, requiresConfirmation: e.target.checked })
            }
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label
            htmlFor="requiresConfirmation"
            className="ml-2 block text-sm text-gray-700"
          >
            Requires host confirmation
          </label>
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => router.push("/")}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create Event Type"}
          </button>
        </div>
      </form>
    </div>
  );
}
