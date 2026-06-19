"use client";

import { useEffect, useState } from "react";
import { listSchedules, createSchedule, addAvailability } from "@/lib/api";
import { Schedule, CreateAvailability } from "@/lib/types";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newScheduleName, setNewScheduleName] = useState("");
  const [newScheduleTimezone, setNewScheduleTimezone] = useState(
    "Europe/Moscow"
  );
  const [selectedSchedule, setSelectedSchedule] = useState<number | null>(null);
  const [availabilityForm, setAvailabilityForm] = useState<CreateAvailability>({
    days: "[0,1,2,3,4]",
    startTime: "09:00",
    endTime: "17:00",
  });
  const [selectedDays, setSelectedDays] = useState<boolean[]>([
    true,
    true,
    true,
    true,
    true,
    false,
    false,
  ]);

  useEffect(() => {
    loadSchedules();
  }, []);

  async function loadSchedules() {
    try {
      const data = await listSchedules();
      setSchedules(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateSchedule(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createSchedule({
        name: newScheduleName,
        timeZone: newScheduleTimezone,
      });
      setNewScheduleName("");
      setShowCreate(false);
      await loadSchedules();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  }

  async function handleAddAvailability(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedSchedule) return;

    const days = selectedDays
      .map((selected, i) => (selected ? i : -1))
      .filter((i) => i >= 0);

    try {
      await addAvailability(selectedSchedule, {
        ...availabilityForm,
        days: JSON.stringify(days),
      });
      await loadSchedules();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add");
    }
  }

  function toggleDay(index: number) {
    const newSelected = [...selectedDays];
    newSelected[index] = !newSelected[index];
    setSelectedDays(newSelected);
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Schedules</h1>
        <button
          onClick={() => setShowCreate(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
        >
          Create Schedule
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {showCreate && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">New Schedule</h2>
          <form onSubmit={handleCreateSchedule} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Name
                </label>
                <input
                  type="text"
                  required
                  value={newScheduleName}
                  onChange={(e) => setNewScheduleName(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Working hours"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Timezone
                </label>
                <input
                  type="text"
                  value={newScheduleTimezone}
                  onChange={(e) => setNewScheduleTimezone(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
              >
                Create
              </button>
            </div>
          </form>
        </div>
      )}

      {loading && (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      )}

      {!loading && schedules.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No schedules yet</p>
        </div>
      )}

      {!loading && schedules.length > 0 && (
        <div className="space-y-6">
          {schedules.map((schedule) => (
            <div
              key={schedule.id}
              className="bg-white border border-gray-200 rounded-lg p-6"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    {schedule.name}
                  </h2>
                  <p className="text-sm text-gray-500">
                    Timezone: {schedule.timeZone}
                  </p>
                </div>
                <button
                  onClick={() =>
                    setSelectedSchedule(
                      selectedSchedule === schedule.id ? null : schedule.id
                    )
                  }
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  {selectedSchedule === schedule.id ? "Cancel" : "Add Availability"}
                </button>
              </div>

              {schedule.availability.length > 0 ? (
                <div className="space-y-2">
                  {schedule.availability.map((avail) => (
                    <div
                      key={avail.id}
                      className="bg-gray-50 rounded-md p-3 text-sm"
                    >
                      <span className="font-medium">
                        {JSON.parse(avail.days)
                          .map((d: number) => DAYS[d])
                          .join(", ")}
                      </span>
                      <span className="text-gray-500 mx-2">|</span>
                      <span>
                        {avail.startTime} - {avail.endTime}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">
                  No availability windows configured
                </p>
              )}

              {selectedSchedule === schedule.id && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <form
                    onSubmit={handleAddAvailability}
                    className="space-y-4"
                  >
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Days
                      </label>
                      <div className="flex space-x-2">
                        {DAYS.map((day, i) => (
                          <button
                            key={day}
                            type="button"
                            onClick={() => toggleDay(i)}
                            className={`px-3 py-1 rounded text-sm ${
                              selectedDays[i]
                                ? "bg-blue-600 text-white"
                                : "bg-gray-200 text-gray-700"
                            }`}
                          >
                            {day}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Start Time
                        </label>
                        <input
                          type="time"
                          value={availabilityForm.startTime}
                          onChange={(e) =>
                            setAvailabilityForm({
                              ...availabilityForm,
                              startTime: e.target.value,
                            })
                          }
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          End Time
                        </label>
                        <input
                          type="time"
                          value={availabilityForm.endTime}
                          onChange={(e) =>
                            setAvailabilityForm({
                              ...availabilityForm,
                              endTime: e.target.value,
                            })
                          }
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                    <button
                      type="submit"
                      className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700"
                    >
                      Add Availability Window
                    </button>
                  </form>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
