import asyncio
from playwright.async_api import async_playwright

RESULT_PATH = "main4_add_expense_results.txt"

# mark started
with open(RESULT_PATH, "w", encoding="utf-8") as f:
    f.write("STARTED\n")


async def run():
    results = []

    def ok(msg):
        results.append("OK: " + msg)
        print("OK: " + msg)

    def fail(msg):
        results.append("FAIL: " + msg)
        print("FAIL: " + msg)

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False, slow_mo=75, args=["--start-fullscreen", "--start-maximized", "--kiosk"])
        context = await browser.new_context(viewport=None, no_viewport=True)
        page = await context.new_page()

        try:
            await page.goto("http://localhost:4200/login")
            ok("Opened /login")

            await page.fill("input[formcontrolname='email']", "daniilsergej.mail@gmail.com")
            await page.fill("input[formcontrolname='password']", "Kami1234")
            ok("Filled credentials")
            await asyncio.sleep(1)
            await page.get_by_role("button", name="Sign In").click()

            # wait for login
            signed = False
            try:
                try:
                    await page.wait_for_url("**/trips", timeout=8000)
                    ok("Signed in")
                    signed = True
                except Exception:
                    elapsed = 0
                    interval = 0.25
                    max_time = 15.0
                    while elapsed < max_time:
                        token = await page.evaluate("() => localStorage.getItem('authToken')")
                        if token:
                            ok("Signed in")
                            signed = True
                            break
                        await asyncio.sleep(interval)
                        elapsed += interval
                    if not signed:
                        fail("Login did not set authToken and did not navigate to /trips")
            except Exception as e:
                fail(f"Login wait failed: {e}")

            # open trips and click the trip card created earlier
            await page.goto("http://localhost:4200/trips")
            ok("Opened /trips")
            # give frontend time to fetch trip participants/payer options
            await asyncio.sleep(5)
            try:
                # fast poll for the trip card to avoid long blocking timeouts
                found = False
                for _ in range(40):
                    if await page.locator("mat-card:has-text('E2E Trip')").count() > 0:
                        found = True
                        break
                    await asyncio.sleep(0.2)
                if not found:
                    raise Exception("E2E Trip card not found")
                trip = page.locator("mat-card:has-text('E2E Trip')").first
                await trip.scroll_into_view_if_needed()
                await trip.click(force=True)
                ok("Opened trip details")
                # wait a bit for trip details / participantShares initialization
                await asyncio.sleep(5)
            except Exception as e:
                fail(f"Open trip failed: {e}")

            # click Add Expense
            try:
                # quick poll and force-click the Add Expense button
                found = False
                for _ in range(30):
                    if await page.locator("button:has-text('Add Expense')").count() > 0:
                        found = True
                        break
                    await asyncio.sleep(0.15)
                if not found:
                    raise Exception("Add Expense button not found")
                await asyncio.sleep(1)
                await page.get_by_role('button', name='Add Expense').first.click(force=True)
                ok("Clicked Add Expense")
            except Exception as e:
                fail(f"Click Add Expense failed: {e}")

            # fill expense form
            try:
                # ensure fields are present quickly, avoid long waits
                found = False
                for _ in range(40):
                    if await page.locator("input[formcontrolname='name']").count() > 0:
                        found = True
                        break
                    await asyncio.sleep(0.15)
                if not found:
                    raise Exception("Expense name input not found")
                await page.fill("input[formcontrolname='name']", "E2E Expense")
                ok("Filled expense name")
                await asyncio.sleep(1)
                await page.fill("textarea[formcontrolname='description']", "Created by automated test")
                ok("Filled expense description")
                await asyncio.sleep(1)
                # robustly fill amount: try multiple selectors and scroll/focus before fill
                amount_value = "123.45"
                filled = False
                selectors = [
                    "input[formcontrolname='amount']",
                    "input[aria-label='Amount']",
                    "input[type='number']",
                    "mat-form-field:has-text('AMOUNT') input",
                ]
                for sel in selectors:
                    try:
                        # fast existence check to avoid long per-selector timeouts
                        if await page.locator(sel).count() == 0:
                            raise Exception("not found")
                        el = page.locator(sel).first
                        await el.scroll_into_view_if_needed()
                        try:
                            await el.click()
                        except Exception:
                            pass
                        await asyncio.sleep(1)
                        await el.fill(amount_value)
                        ok(f"Filled amount using {sel}")
                        filled = True
                        break
                    except Exception:
                        await asyncio.sleep(0.15)
                        continue
                if not filled:
                    # final fallback: try focusing by label and typing
                    try:
                        lbl = await page.locator("label:has-text('AMOUNT')").first
                        await lbl.scroll_into_view_if_needed()
                        await lbl.click()
                        await page.keyboard.type(amount_value)
                        ok("Filled amount using label fallback")
                        filled = True
                    except Exception as e:
                        # capture debug artifacts to help investigate missing element
                        try:
                            await page.screenshot(path="debug_expense_missing_amount.png", full_page=True)
                        except Exception:
                            pass
                        try:
                            html = await page.content()
                            with open("debug_expense_missing_amount.html", "w", encoding="utf-8") as hf:
                                hf.write(html)
                        except Exception:
                            pass
                        raise Exception(f"Could not find amount input: {e} (saved debug_expense_missing_amount.*)")

                # select Paid By -> Kami (or accept if already User #23)
                try:
                    paid_field = page.locator("mat-form-field:has-text('PAID BY')")
                    await paid_field.scroll_into_view_if_needed()
                    # try to read currently selected text
                    selected_text = None
                    try:
                        selected_text = (await paid_field.locator('.mat-select-value-text').inner_text()).strip()
                    except Exception:
                        selected_text = None

                    if selected_text and ("User #23" in selected_text or "Kami" in selected_text):
                        ok(f"Paid-by already selected: {selected_text}")
                    else:
                        # open paid-by select and select automatically without long waits
                        await page.locator("mat-form-field:has-text('PAID BY') mat-select").first.click(force=True)
                        await asyncio.sleep(1)
                        chosen = False
                        # wait shortly for options to appear, then try preferred texts
                        for opt_text in ("Kami", "User #23"):
                            for _ in range(30):
                                if await page.locator(f"mat-option:has-text('{opt_text}')").count() > 0:
                                    await asyncio.sleep(1)
                                    await page.locator(f"mat-option:has-text('{opt_text}')").first.click(force=True)
                                    ok(f"Selected paid by {opt_text}")
                                    chosen = True
                                    break
                                await asyncio.sleep(0.12)
                            if chosen:
                                break
                        if not chosen:
                            # click first visible option immediately
                            try:
                                if await page.locator('mat-option').count() > 0:
                                    await asyncio.sleep(1)
                                    await page.locator('mat-option').first.click(force=True)
                                    ok("Selected paid by (first available)")
                                else:
                                    raise Exception("No mat-option items found")
                            except Exception as e:
                                fail(f"Select paid by failed: {e}")
                except Exception as e:
                    fail(f"Select paid by failed: {e}")

                # ensure participants checkboxes are checked
                try:
                    # wait for participant list to render
                    # short poll for participants container
                    found = False
                    for _ in range(40):
                        if await page.locator('.participant-list').count() > 0:
                            found = True
                            break
                        await asyncio.sleep(0.15)
                    if not found:
                        raise Exception('participant list not found')
                    # select all participant checkboxes by clicking the accessible checkbox in each participant-item
                    items = page.locator('.participant-list .participant-item')
                    count = await items.count()
                    for i in range(count):
                        item = items.nth(i)
                        try:
                            await item.scroll_into_view_if_needed()
                        except Exception:
                            pass

                        # Try the accessible checkbox first
                        try:
                            checkbox = item.get_by_role('checkbox')
                            try:
                                checked = await checkbox.get_attribute('aria-checked')
                            except Exception:
                                checked = None
                            if checked != 'true':
                                await asyncio.sleep(1)
                                await checkbox.click(force=True)
                        except Exception:
                            # fallback: click any mat-checkbox element inside
                            try:
                                inner = item.locator('mat-checkbox')
                                if await inner.count() > 0:
                                    await inner.first.click(force=True)
                            except Exception:
                                pass
                    ok("Selected participants")
                except Exception as e:
                    fail(f"Select participants failed: {e}")

                # submit
                try:
                    await page.get_by_role('button', name='Add Expense').click()
                    ok("Clicked Add Expense submit")
                    # wait for UI to process the submission and update
                    try:
                        await asyncio.sleep(7)
                        ok("Post-submit wait finished")
                    except Exception:
                        pass
                except Exception as e:
                    fail(f"Submit Add Expense failed: {e}")

            except Exception as e:
                fail(f"Expense form failed: {e}")

        except Exception as e:
            fail(f"Script error: {e}")
        finally:
            try:
                await context.close()
            except Exception:
                pass
            try:
                await browser.close()
            except Exception:
                pass

    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        for r in results:
            f.write(r + "\n")
        f.write("DONE\n")


if __name__ == '__main__':
    asyncio.run(run())
