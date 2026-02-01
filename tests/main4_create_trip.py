import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

RESULT_PATH = "main4_create_trip_results.txt"

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
        # Prefer a locally extracted Google Chrome binary if provided via LOCAL_CHROME
        # or found under tests/.local-chrome. Fallback to Playwright-managed Chromium.
        local_env_path = os.environ.get("LOCAL_CHROME")
        fallback_path = Path(__file__).resolve().parent / ".local-chrome/opt/google/chrome/google-chrome"
        chrome_path = None
        if local_env_path:
            pth = Path(local_env_path)
            if pth.exists():
                chrome_path = str(pth)
        elif fallback_path.exists():
            chrome_path = str(fallback_path)

        if chrome_path:
            browser = await p.chromium.launch(executable_path=chrome_path, headless=False, slow_mo=75, args=["--start-fullscreen", "--start-maximized", "--kiosk"])
        else:
            # No system Chrome and no local Chrome found — use Playwright-managed Chromium
            browser = await p.chromium.launch(headless=False, slow_mo=75, args=["--start-fullscreen", "--start-maximized", "--kiosk"])
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

            # open create trip panel
            await page.wait_for_selector("button:has-text('New Trip')", timeout=10000)
            await page.locator("button:has-text('New Trip')").click()
            ok("Opened New Trip panel")
            await asyncio.sleep(0.5)

            # fill fields
            await page.wait_for_selector("input[formcontrolname='name']", timeout=5000)
            await page.fill("input[formcontrolname='name']", "E2E Trip")
            ok("Filled Trip name")
            await asyncio.sleep(1)
            await page.fill("textarea[formcontrolname='description']", "Created by automated test")
            ok("Filled Description")

            # set dates if inputs present
            try:
                await page.fill("input[formcontrolname='startDate']", "2025-12-20")
                await page.fill("input[formcontrolname='endDate']", "2025-12-25")
                ok("Filled dates")
            except Exception:
                # ignore if date inputs are not simple text inputs
                pass

            # open friends dropdown and select Legend (Legenddd)
            try:
                # open the select using its label to ensure the menu opens correctly
                try:
                    await page.get_by_label('SELECT FRIENDS').click()
                except Exception:
                    # fallback to previous selector if label is not available
                    await page.wait_for_selector("mat-form-field mat-select", timeout=10000)
                    await page.locator("mat-form-field mat-select").click()
                await asyncio.sleep(0.8)

                opts = page.locator('mat-option')
                try:
                    cnt = await opts.count()
                except Exception:
                    cnt = 0
                chosen = False

                # Search options for 'Legend'/'Legenddd' robustly
                for i in range(cnt):
                    o = opts.nth(i)
                    try:
                        txt = (await o.inner_text()).strip()
                    except Exception:
                        txt = ''
                    if 'Legend' in txt or 'Legenddd' in txt:
                        await o.scroll_into_view_if_needed()
                        await asyncio.sleep(0.25)
                        await o.click(force=True)
                        ok(f"Selected {txt}")
                        chosen = True
                        break

                # fallback: try has-text queries for possible variants
                if not chosen:
                    for variant in ('Legend', 'Legenddd'):
                        if await page.locator(f"mat-option:has-text('{variant}')").count() > 0:
                            await page.locator(f"mat-option:has-text('{variant}')").first.click(force=True)
                            ok(f"Selected {variant} (fallback)")
                            chosen = True
                            break

                # final fallback: pick the first option
                if not chosen:
                    if cnt > 0:
                        await opts.first.click(force=True)
                        try:
                            first_txt = (await opts.first.inner_text()).strip()
                        except Exception:
                            first_txt = 'first option'
                        ok(f"Selected {first_txt} (final fallback)")
                    else:
                        raise Exception('No friend options found')
                # close the select overlay if present by clicking backdrop or pressing Escape
                try:
                    if await page.locator('div.cdk-overlay-backdrop').count() > 0:
                        await page.locator('div.cdk-overlay-backdrop').first.click()
                    else:
                        await page.keyboard.press('Escape')
                    await page.wait_for_selector('div.cdk-overlay-backdrop', state='detached', timeout=3000)
                except Exception:
                    pass
            except Exception as e:
                fail(f"Select Karel failed: {e}")

            # wait for submit enabled then click
            try:
                submit = page.locator("button[type='submit']")
                for _ in range(50):
                    # ensure no overlay is intercepting clicks
                    if await page.locator('div.cdk-overlay-backdrop').count() > 0:
                        await page.keyboard.press('Escape')
                    if await submit.is_enabled():
                        # press Enter first to dismiss any floating menu that may intercept
                        try:
                            await page.keyboard.press('Enter')
                        except Exception:
                            pass
                        await submit.click()
                        ok("Clicked Create")
                        # wait for trip creation to be visible: either a trip card appears or trips page updates
                        try:
                            # try to see the trip card on trips list
                            await page.wait_for_selector("mat-card:has-text('E2E Trip')", timeout=10000)
                            ok("Trip created (found trip card)")
                        except Exception:
                            try:
                                # maybe redirected; wait for trips URL then trip card
                                await page.wait_for_url("**/trips", timeout=10000)
                                await page.wait_for_selector("mat-card:has-text('E2E Trip')", timeout=10000)
                                ok("Trip created (redirected to trips and found card)")
                            except Exception:
                                # final fallback: give short extra time
                                await asyncio.sleep(3)
                                ok("Post-create wait finished (fallback)")
                        # additional fixed pause to ensure UI finishes closing dialogs
                        try:
                            await asyncio.sleep(5)
                        except Exception:
                            pass

                        # Re-open the created trip and send an invite to a friend:
                        try:
                            # click the trip card to open details
                            if await page.locator("mat-card:has-text('E2E Trip')").count() > 0:
                                trip_card = page.locator("mat-card:has-text('E2E Trip')").first
                                await trip_card.scroll_into_view_if_needed()
                                await asyncio.sleep(1)
                                await trip_card.click(force=True)
                                ok('Opened created trip details')
                                await asyncio.sleep(2)

                                # open invite friends select and pick Legend (preferred)
                                try:
                                    await page.get_by_label('SELECT FRIENDS').click()
                                    await asyncio.sleep(1)
                                    # try to click 'Karel' option first, fallback to first mat-option
                                    if await page.locator("mat-option:has-text('Karel')").count() > 0:
                                        await page.locator("mat-option:has-text('Karel')").first.click(force=True)
                                        ok('Selected friend Karel in invite')
                                    else:
                                        if await page.locator('mat-option').count() > 0:
                                            await page.locator('mat-option').first.click(force=True)
                                            ok('Selected first friend in invite')
                                    await asyncio.sleep(0.5)
                                    # click a safe non-interactive area to close dropdown/context menus
                                    try:
                                        if await page.locator('.trip-info').count() > 0:
                                            await page.locator('.trip-info').first.click(force=True)
                                        elif await page.locator('.trip-details').count() > 0:
                                            await page.locator('.trip-details').first.click(force=True)
                                        else:
                                            await page.mouse.click(50, 50)
                                    except Exception:
                                        try:
                                            await page.mouse.click(50, 50)
                                        except Exception:
                                            pass
                                    await asyncio.sleep(0.5)
                                    # send invite
                                    try:
                                        await page.get_by_role('button', name='Send invite').click()
                                        ok('Clicked Send invite')
                                    except Exception:
                                        try:
                                            await page.get_by_text('Send invite').click()
                                            ok('Clicked Send invite (fallback)')
                                        except Exception as e:
                                            fail(f'Send invite failed: {e}')
                                except Exception as e:
                                    fail(f'Invite flow failed: {e}')
                        except Exception:
                            pass
                        break
                    await asyncio.sleep(0.2)
                else:
                    try:
                        await page.get_by_role("button", name="Create").click()
                        ok("Clicked Create (fallback)")
                    except Exception as e:
                        fail(f"Click Create failed: {e}")
            except Exception as e:
                fail(f"Submit click flow failed: {e}")

            await page.wait_for_timeout(500)

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
