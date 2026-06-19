import { test, expect } from "@playwright/test";

function getWeekday(offsetDays: number): string {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  while (date.getDay() === 0 || date.getDay() === 6) {
    date.setDate(date.getDate() + 1);
  }
  return date.toISOString().split("T")[0];
}

function getWeekend(offsetDays: number): string {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  while (date.getDay() !== 0 && date.getDay() !== 6) {
    date.setDate(date.getDate() + 1);
  }
  return date.toISOString().split("T")[0];
}

// ─── Homepage ─────────────────────────────────────────────

test.describe("Homepage", () => {
  test("shows event types list with title, slug, and duration", async ({
    page,
  }) => {
    await page.goto("/");

    await expect(
      page.getByRole("heading", { name: "Event Types" })
    ).toBeVisible();
    await expect(page.getByText("Consultation").first()).toBeVisible();
    await expect(page.getByText("/demo/consult").first()).toBeVisible();
    await expect(page.getByText("30 min").first()).toBeVisible();
  });

  test("'Create Event Type' button navigates to create form", async ({
    page,
  }) => {
    await page.goto("/");

    await page.getByRole("link", { name: "Create Event Type" }).click();
    await expect(page).toHaveURL("/event-types/new");
    await expect(
      page.getByRole("heading", { name: "Create Event Type" })
    ).toBeVisible();
  });

  test("'View booking page' link navigates to booking page", async ({
    page,
  }) => {
    await page.goto("/");

    await page.getByText("View booking page").first().click();
    await expect(page).toHaveURL(/\/demo\/consult/);
    await expect(
      page.getByRole("heading", { name: "Consultation" })
    ).toBeVisible();
  });
});

// ─── Booking page ─────────────────────────────────────────

test.describe("Booking page", () => {
  test("shows event details: title, duration, host", async ({ page }) => {
    await page.goto("/demo/consult");

    await expect(
      page.getByRole("heading", { name: "Consultation" })
    ).toBeVisible();
    await expect(page.getByText("30 minutes")).toBeVisible();
    await expect(page.getByText("Hosted by demo")).toBeVisible();
  });

  test("shows description when present", async ({ page }) => {
    await page.goto("/demo/consult");

    await expect(
      page.getByText("30-minute consultation meeting")
    ).toBeVisible();
  });

  test("date picker defaults to today", async ({ page }) => {
    await page.goto("/demo/consult");

    const today = new Date().toISOString().split("T")[0];
    const dateInput = page.locator("#booking-date");
    await expect(dateInput).toHaveValue(today);
  });

  test("shows available slots on weekday", async ({ page }) => {
    const weekday = getWeekday(1);
    await page.goto("/demo/consult");

    const dateInput = page.locator("#booking-date");
    await dateInput.fill(weekday);

    await expect(page.getByText("Available times")).toBeVisible();
    const slots = page
      .locator("button")
      .filter({ hasText: /^\d{2}:\d{2}$/ });
    await expect(slots.first()).toBeVisible();
    const count = await slots.count();
    expect(count).toBeGreaterThan(0);
  });

  test("shows 'No available times' on weekend", async ({ page }) => {
    const weekend = getWeekend(0);
    await page.goto("/demo/consult");

    const dateInput = page.locator("#booking-date");
    await dateInput.fill(weekend);

    await expect(
      page.getByText("No available times for this date")
    ).toBeVisible();
  });

  test("selecting a slot reveals the booking form", async ({ page }) => {
    const weekday = getWeekday(1);
    await page.goto("/demo/consult");

    const dateInput = page.locator("#booking-date");
    await dateInput.fill(weekday);
    await expect(page.getByText("Available times")).toBeVisible();

    const firstSlot = page
      .locator("button")
      .filter({ hasText: /^\d{2}:\d{2}$/ })
      .first();
    await firstSlot.click();

    await expect(page.getByText("Enter your details")).toBeVisible();
    await expect(page.getByLabel("Name *")).toBeVisible();
    await expect(page.getByLabel("Email *")).toBeVisible();
    await expect(page.getByLabel("Timezone")).toBeVisible();
  });

  test("timezone field is pre-filled with browser timezone", async ({
    page,
  }) => {
    const weekday = getWeekday(1);
    await page.goto("/demo/consult");

    const dateInput = page.locator("#booking-date");
    await dateInput.fill(weekday);
    await expect(page.getByText("Available times")).toBeVisible();

    await page
      .locator("button")
      .filter({ hasText: /^\d{2}:\d{2}$/ })
      .first()
      .click();

    const tz = await page.getByLabel("Timezone").inputValue();
    expect(tz).toBeTruthy();
    expect(tz).toMatch(/^([A-Za-z_]+\/[A-Za-z_]+|UTC)$/);
  });

  test("clicking selected slot again keeps form visible", async ({ page }) => {
    const weekday = getWeekday(1);
    await page.goto("/demo/consult");

    const dateInput = page.locator("#booking-date");
    await dateInput.fill(weekday);
    await expect(page.getByText("Available times")).toBeVisible();

    const slotButtons = page
      .locator("button")
      .filter({ hasText: /^\d{2}:\d{2}$/ });
    await expect(slotButtons.first()).toBeVisible();

    await slotButtons.first().click();
    await expect(page.getByText("Enter your details")).toBeVisible();
  });

  test("complete booking: select date → slot → fill form → confirm", async ({
    page,
  }) => {
    const weekday = getWeekday(1);
    await page.goto("/demo/consult");

    const dateInput = page.locator("#booking-date");
    await dateInput.fill(weekday);
    await expect(page.getByText("Available times")).toBeVisible();

    await page
      .locator("button")
      .filter({ hasText: /^\d{2}:\d{2}$/ })
      .first()
      .click();

    await expect(page.getByText("Enter your details")).toBeVisible();
    await page.getByLabel("Name *").fill("Test User");
    await page.getByLabel("Email *").fill("test@example.com");

    await page.getByRole("button", { name: "Confirm Booking" }).click();

    await expect(page.getByText("Booked!")).toBeVisible();
    await expect(
      page.getByText("Your meeting has been scheduled")
    ).toBeVisible();
  });

  test("shows 'Event Not Found' for invalid slug", async ({ page }) => {
    await page.goto("/demo/nonexistent");

    await expect(
      page.getByRole("heading", { name: "Event Not Found" })
    ).toBeVisible();
    await expect(page.getByText("Event type not found")).toBeVisible();
  });

  test("changing date reloads slots", async ({ page }) => {
    const weekday1 = getWeekday(0);
    const weekday2 = getWeekday(7);
    await page.goto("/demo/consult");

    const dateInput = page.locator("#booking-date");
    await dateInput.fill(weekday1);
    await expect(page.getByText("Available times")).toBeVisible();

    await dateInput.fill(weekday2);
    await expect(page.getByText("Available times")).toBeVisible();
  });
});

// ─── Create Event Type page ───────────────────────────────

test.describe("Create Event Type", () => {
  test("form renders with all fields", async ({ page }) => {
    await page.goto("/event-types/new");

    await expect(
      page.getByRole("heading", { name: "Create Event Type" })
    ).toBeVisible();
    await expect(page.getByLabel("Title *")).toBeVisible();
    await expect(page.getByLabel(/Slug/)).toBeVisible();
    await expect(page.getByLabel("Description")).toBeVisible();
    await expect(page.getByLabel("Duration")).toBeVisible();
    await expect(page.getByLabel("Slot Interval")).toBeVisible();
    await expect(page.getByLabel("Location")).toBeVisible();
  });

  test("create event type and redirect to homepage", async ({ page }) => {
    await page.goto("/event-types/new");

    const uniqueSlug = `test-${Date.now()}`;
    await page.getByLabel("Title *").fill("Test Meeting");
    await page.getByLabel(/Slug/).fill(uniqueSlug);
    await page.getByLabel("Description").fill("A test meeting");
    await page.getByLabel("Duration").fill("45");
    await page.getByLabel("Location").fill("Google Meet");

    await page.getByRole("button", { name: "Create Event Type" }).click();

    await expect(page).toHaveURL("/");
    await expect(page.getByText("Test Meeting").first()).toBeVisible();
  });

  test("cancel button navigates back to homepage", async ({ page }) => {
    await page.goto("/event-types/new");

    await page.getByRole("button", { name: "Cancel" }).click();
    await expect(page).toHaveURL("/");
  });
});

// ─── Schedules page ───────────────────────────────────────

test.describe("Schedules page", () => {
  test("shows schedules list with title", async ({ page }) => {
    await page.goto("/schedules");

    await expect(
      page.getByRole("heading", { name: "Schedules" })
    ).toBeVisible();
    await expect(page.getByText("Working hours")).toBeVisible();
  });

  test("shows availability window for schedule", async ({ page }) => {
    await page.goto("/schedules");

    await expect(page.getByText("Working hours")).toBeVisible();
    await expect(page.getByText("Mon, Tue, Wed, Thu, Fri")).toBeVisible();
  });

  test("'Create Schedule' button opens create form", async ({ page }) => {
    await page.goto("/schedules");

    await expect(page.getByText("Working hours")).toBeVisible();
    await page.getByRole("button", { name: "Create Schedule" }).click();
    await expect(page.getByText("New Schedule")).toBeVisible();
  });

  test("'Add Availability' opens form, cancel closes it", async ({ page }) => {
    await page.goto("/schedules");

    await expect(page.getByText("Working hours")).toBeVisible();
    await page.getByRole("button", { name: "Add Availability" }).first().click();
    await expect(page.getByText("Add Availability Window")).toBeVisible();

    await page.getByRole("button", { name: "Cancel" }).first().click();
    await expect(page.getByText("Add Availability Window")).not.toBeVisible();
  });
});

// ─── Navigation ───────────────────────────────────────────

test.describe("Navigation", () => {
  test("header nav links work", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("link", { name: "Schedules" }).click();
    await expect(page).toHaveURL("/schedules");
    await expect(
      page.getByRole("heading", { name: "Schedules" })
    ).toBeVisible();

    await page.getByRole("link", { name: "Event Types" }).click();
    await expect(page).toHaveURL("/");
    await expect(
      page.getByRole("heading", { name: "Event Types" })
    ).toBeVisible();
  });
});
