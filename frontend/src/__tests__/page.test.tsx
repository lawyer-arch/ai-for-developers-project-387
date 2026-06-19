import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Home from "@/app/page";
import { listEventTypes } from "@/lib/api";

vi.mock("@/lib/api");

const mockListEventTypes = vi.mocked(listEventTypes);

describe("Home Page", () => {
  beforeEach(() => {
    mockListEventTypes.mockClear();
  });

  it("renders loading state", () => {
    mockListEventTypes.mockImplementation(() => new Promise(() => {}));
    render(<Home />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders event types list", async () => {
    mockListEventTypes.mockResolvedValue([
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
    ]);

    render(<Home />);

    await waitFor(() => {
      expect(screen.getByText("Consultation")).toBeInTheDocument();
    });
    expect(screen.getByText("/demo/consult")).toBeInTheDocument();
    expect(screen.getByText("Duration: 30 min")).toBeInTheDocument();
  });

  it("renders empty state", async () => {
    mockListEventTypes.mockResolvedValue([]);

    render(<Home />);

    await waitFor(() => {
      expect(screen.getByText("No event types yet")).toBeInTheDocument();
    });
  });

  it("renders error state", async () => {
    mockListEventTypes.mockRejectedValue(new Error("Network error"));

    render(<Home />);

    await waitFor(() => {
      expect(screen.getByText("Network error")).toBeInTheDocument();
    });
  });

  it("has link to create event type", async () => {
    mockListEventTypes.mockResolvedValue([]);

    render(<Home />);

    await waitFor(() => {
      const links = screen.getAllByRole("link", { name: /create event type/i });
      expect(links.length).toBeGreaterThanOrEqual(1);
      expect(links[0]).toHaveAttribute("href", "/event-types/new");
    });
  });
});
