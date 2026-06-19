# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: booking.spec.ts >> Homepage >> 'View booking page' link navigates to booking page
- Location: tests/e2e/booking.spec.ts:49:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/
Call log:
  - navigating to "http://localhost:3000/", waiting until "load"

```

# Test source

```ts
  1   | import { test, expect } from "@playwright/test";
  2   | 
  3   | function getWeekday(offsetDays: number): string {
  4   |   const date = new Date();
  5   |   date.setDate(date.getDate() + offsetDays);
  6   |   while (date.getDay() === 0 || date.getDay() === 6) {
  7   |     date.setDate(date.getDate() + 1);
  8   |   }
  9   |   return date.toISOString().split("T")[0];
  10  | }
  11  | 
  12  | function getWeekend(offsetDays: number): string {
  13  |   const date = new Date();
  14  |   date.setDate(date.getDate() + offsetDays);
  15  |   while (date.getDay() !== 0 && date.getDay() !== 6) {
  16  |     date.setDate(date.getDate() + 1);
  17  |   }
  18  |   return date.toISOString().split("T")[0];
  19  | }
  20  | 
  21  | // ─── Homepage ─────────────────────────────────────────────
  22  | 
  23  | test.describe("Homepage", () => {
  24  |   test("shows event types list with title, slug, and duration", async ({
  25  |     page,
  26  |   }) => {
  27  |     await page.goto("/");
  28  | 
  29  |     await expect(
  30  |       page.getByRole("heading", { name: "Event Types" })
  31  |     ).toBeVisible();
  32  |     await expect(page.getByText("Consultation").first()).toBeVisible();
  33  |     await expect(page.getByText("/demo/consult").first()).toBeVisible();
  34  |     await expect(page.getByText("30 min").first()).toBeVisible();
  35  |   });
  36  | 
  37  |   test("'Create Event Type' button navigates to create form", async ({
  38  |     page,
  39  |   }) => {
  40  |     await page.goto("/");
  41  | 
  42  |     await page.getByRole("link", { name: "Create Event Type" }).click();
  43  |     await expect(page).toHaveURL("/event-types/new");
  44  |     await expect(
  45  |       page.getByRole("heading", { name: "Create Event Type" })
  46  |     ).toBeVisible();
  47  |   });
  48  | 
  49  |   test("'View booking page' link navigates to booking page", async ({
  50  |     page,
  51  |   }) => {
> 52  |     await page.goto("/");
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/
  53  | 
  54  |     await page.getByText("View booking page").first().click();
  55  |     await expect(page).toHaveURL(/\/demo\/consult/);
  56  |     await expect(
  57  |       page.getByRole("heading", { name: "Consultation" })
  58  |     ).toBeVisible();
  59  |   });
  60  | });
  61  | 
  62  | // ─── Booking page ─────────────────────────────────────────
  63  | 
  64  | test.describe("Booking page", () => {
  65  |   test("shows event details: title, duration, host", async ({ page }) => {
  66  |     await page.goto("/demo/consult");
  67  | 
  68  |     await expect(
  69  |       page.getByRole("heading", { name: "Consultation" })
  70  |     ).toBeVisible();
  71  |     await expect(page.getByText("30 minutes")).toBeVisible();
  72  |     await expect(page.getByText("Hosted by demo")).toBeVisible();
  73  |   });
  74  | 
  75  |   test("shows description when present", async ({ page }) => {
  76  |     await page.goto("/demo/consult");
  77  | 
  78  |     await expect(
  79  |       page.getByText("30-minute consultation meeting")
  80  |     ).toBeVisible();
  81  |   });
  82  | 
  83  |   test("date picker defaults to today", async ({ page }) => {
  84  |     await page.goto("/demo/consult");
  85  | 
  86  |     const today = new Date().toISOString().split("T")[0];
  87  |     const dateInput = page.locator("#booking-date");
  88  |     await expect(dateInput).toHaveValue(today);
  89  |   });
  90  | 
  91  |   test("shows available slots on weekday", async ({ page }) => {
  92  |     const weekday = getWeekday(1);
  93  |     await page.goto("/demo/consult");
  94  | 
  95  |     const dateInput = page.locator("#booking-date");
  96  |     await dateInput.fill(weekday);
  97  | 
  98  |     await expect(page.getByText("Available times")).toBeVisible();
  99  |     const slots = page
  100 |       .locator("button")
  101 |       .filter({ hasText: /^\d{2}:\d{2}$/ });
  102 |     await expect(slots.first()).toBeVisible();
  103 |     const count = await slots.count();
  104 |     expect(count).toBeGreaterThan(0);
  105 |   });
  106 | 
  107 |   test("shows 'No available times' on weekend", async ({ page }) => {
  108 |     const weekend = getWeekend(0);
  109 |     await page.goto("/demo/consult");
  110 | 
  111 |     const dateInput = page.locator("#booking-date");
  112 |     await dateInput.fill(weekend);
  113 | 
  114 |     await expect(
  115 |       page.getByText("No available times for this date")
  116 |     ).toBeVisible();
  117 |   });
  118 | 
  119 |   test("selecting a slot reveals the booking form", async ({ page }) => {
  120 |     const weekday = getWeekday(1);
  121 |     await page.goto("/demo/consult");
  122 | 
  123 |     const dateInput = page.locator("#booking-date");
  124 |     await dateInput.fill(weekday);
  125 |     await expect(page.getByText("Available times")).toBeVisible();
  126 | 
  127 |     const firstSlot = page
  128 |       .locator("button")
  129 |       .filter({ hasText: /^\d{2}:\d{2}$/ })
  130 |       .first();
  131 |     await firstSlot.click();
  132 | 
  133 |     await expect(page.getByText("Enter your details")).toBeVisible();
  134 |     await expect(page.getByLabel("Name *")).toBeVisible();
  135 |     await expect(page.getByLabel("Email *")).toBeVisible();
  136 |     await expect(page.getByLabel("Timezone")).toBeVisible();
  137 |   });
  138 | 
  139 |   test("timezone field is pre-filled with browser timezone", async ({
  140 |     page,
  141 |   }) => {
  142 |     const weekday = getWeekday(1);
  143 |     await page.goto("/demo/consult");
  144 | 
  145 |     const dateInput = page.locator("#booking-date");
  146 |     await dateInput.fill(weekday);
  147 |     await expect(page.getByText("Available times")).toBeVisible();
  148 | 
  149 |     await page
  150 |       .locator("button")
  151 |       .filter({ hasText: /^\d{2}:\d{2}$/ })
  152 |       .first()
```