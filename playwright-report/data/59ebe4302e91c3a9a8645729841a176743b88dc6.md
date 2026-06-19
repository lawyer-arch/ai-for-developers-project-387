# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: booking.spec.ts >> Schedules page >> 'Add Availability' opens form, cancel closes it
- Location: tests/e2e/booking.spec.ts:296:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/schedules
Call log:
  - navigating to "http://localhost:3000/schedules", waiting until "load"

```

# Test source

```ts
  197 |     await page.getByRole("button", { name: "Confirm Booking" }).click();
  198 | 
  199 |     await expect(page.getByText("Booked!")).toBeVisible();
  200 |     await expect(
  201 |       page.getByText("Your meeting has been scheduled")
  202 |     ).toBeVisible();
  203 |   });
  204 | 
  205 |   test("shows 'Event Not Found' for invalid slug", async ({ page }) => {
  206 |     await page.goto("/demo/nonexistent");
  207 | 
  208 |     await expect(
  209 |       page.getByRole("heading", { name: "Event Not Found" })
  210 |     ).toBeVisible();
  211 |     await expect(page.getByText("Event type not found")).toBeVisible();
  212 |   });
  213 | 
  214 |   test("changing date reloads slots", async ({ page }) => {
  215 |     const weekday1 = getWeekday(0);
  216 |     const weekday2 = getWeekday(7);
  217 |     await page.goto("/demo/consult");
  218 | 
  219 |     const dateInput = page.locator("#booking-date");
  220 |     await dateInput.fill(weekday1);
  221 |     await expect(page.getByText("Available times")).toBeVisible();
  222 | 
  223 |     await dateInput.fill(weekday2);
  224 |     await expect(page.getByText("Available times")).toBeVisible();
  225 |   });
  226 | });
  227 | 
  228 | // ─── Create Event Type page ───────────────────────────────
  229 | 
  230 | test.describe("Create Event Type", () => {
  231 |   test("form renders with all fields", async ({ page }) => {
  232 |     await page.goto("/event-types/new");
  233 | 
  234 |     await expect(
  235 |       page.getByRole("heading", { name: "Create Event Type" })
  236 |     ).toBeVisible();
  237 |     await expect(page.getByLabel("Title *")).toBeVisible();
  238 |     await expect(page.getByLabel(/Slug/)).toBeVisible();
  239 |     await expect(page.getByLabel("Description")).toBeVisible();
  240 |     await expect(page.getByLabel("Duration")).toBeVisible();
  241 |     await expect(page.getByLabel("Slot Interval")).toBeVisible();
  242 |     await expect(page.getByLabel("Location")).toBeVisible();
  243 |   });
  244 | 
  245 |   test("create event type and redirect to homepage", async ({ page }) => {
  246 |     await page.goto("/event-types/new");
  247 | 
  248 |     const uniqueSlug = `test-${Date.now()}`;
  249 |     await page.getByLabel("Title *").fill("Test Meeting");
  250 |     await page.getByLabel(/Slug/).fill(uniqueSlug);
  251 |     await page.getByLabel("Description").fill("A test meeting");
  252 |     await page.getByLabel("Duration").fill("45");
  253 |     await page.getByLabel("Location").fill("Google Meet");
  254 | 
  255 |     await page.getByRole("button", { name: "Create Event Type" }).click();
  256 | 
  257 |     await expect(page).toHaveURL("/");
  258 |     await expect(page.getByText("Test Meeting").first()).toBeVisible();
  259 |   });
  260 | 
  261 |   test("cancel button navigates back to homepage", async ({ page }) => {
  262 |     await page.goto("/event-types/new");
  263 | 
  264 |     await page.getByRole("button", { name: "Cancel" }).click();
  265 |     await expect(page).toHaveURL("/");
  266 |   });
  267 | });
  268 | 
  269 | // ─── Schedules page ───────────────────────────────────────
  270 | 
  271 | test.describe("Schedules page", () => {
  272 |   test("shows schedules list with title", async ({ page }) => {
  273 |     await page.goto("/schedules");
  274 | 
  275 |     await expect(
  276 |       page.getByRole("heading", { name: "Schedules" })
  277 |     ).toBeVisible();
  278 |     await expect(page.getByText("Working hours")).toBeVisible();
  279 |   });
  280 | 
  281 |   test("shows availability window for schedule", async ({ page }) => {
  282 |     await page.goto("/schedules");
  283 | 
  284 |     await expect(page.getByText("Working hours")).toBeVisible();
  285 |     await expect(page.getByText("Mon, Tue, Wed, Thu, Fri")).toBeVisible();
  286 |   });
  287 | 
  288 |   test("'Create Schedule' button opens create form", async ({ page }) => {
  289 |     await page.goto("/schedules");
  290 | 
  291 |     await expect(page.getByText("Working hours")).toBeVisible();
  292 |     await page.getByRole("button", { name: "Create Schedule" }).click();
  293 |     await expect(page.getByText("New Schedule")).toBeVisible();
  294 |   });
  295 | 
  296 |   test("'Add Availability' opens form, cancel closes it", async ({ page }) => {
> 297 |     await page.goto("/schedules");
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/schedules
  298 | 
  299 |     await expect(page.getByText("Working hours")).toBeVisible();
  300 |     await page.getByRole("button", { name: "Add Availability" }).first().click();
  301 |     await expect(page.getByText("Add Availability Window")).toBeVisible();
  302 | 
  303 |     await page.getByRole("button", { name: "Cancel" }).first().click();
  304 |     await expect(page.getByText("Add Availability Window")).not.toBeVisible();
  305 |   });
  306 | });
  307 | 
  308 | // ─── Navigation ───────────────────────────────────────────
  309 | 
  310 | test.describe("Navigation", () => {
  311 |   test("header nav links work", async ({ page }) => {
  312 |     await page.goto("/");
  313 | 
  314 |     await page.getByRole("link", { name: "Schedules" }).click();
  315 |     await expect(page).toHaveURL("/schedules");
  316 |     await expect(
  317 |       page.getByRole("heading", { name: "Schedules" })
  318 |     ).toBeVisible();
  319 | 
  320 |     await page.getByRole("link", { name: "Event Types" }).click();
  321 |     await expect(page).toHaveURL("/");
  322 |     await expect(
  323 |       page.getByRole("heading", { name: "Event Types" })
  324 |     ).toBeVisible();
  325 |   });
  326 | });
  327 | 
```