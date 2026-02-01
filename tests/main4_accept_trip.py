import asyncio
from playwright.async_api import async_playwright

RESULT_PATH = "main4_accept_trip_results.txt"

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

            await page.fill("input[formcontrolname='email']", "hadenkarel@gmail.com")
            await page.fill("input[formcontrolname='password']", "Karel123")
            ok("Filled Karel credentials")
            await asyncio.sleep(1)
            await page.get_by_role("button", name="Sign In").click()

            # wait for login by navigation or localStorage
            signed = False
            try:
                try:
                    await page.wait_for_url("**/trips", timeout=8000)
                    ok("Signed in as Karel")
                    signed = True
                except Exception:
                    elapsed = 0
                    interval = 0.25
                    max_time = 15.0
                    while elapsed < max_time:
                        token = await page.evaluate("() => localStorage.getItem('authToken')")
                        if token:
                            ok("Signed in as Karel")
                            signed = True
                            break
                        await asyncio.sleep(interval)
                        elapsed += interval
                    if not signed:
                        fail("Login did not set authToken and did not navigate to /trips")
            except Exception as e:
                fail(f"Login wait failed: {e}")

            # open friends (trip invites are shown there)
            await page.goto("http://localhost:4200/friends")
            ok("Opened /friends (Karel)")

            # wait for Join button in Trip Invites and click the first one
            try:
                await page.wait_for_selector("button:has-text('Join')", timeout=3000)
                join_btn = page.locator("button:has-text('Join')").first
                await join_btn.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await join_btn.click()
                ok("Clicked Join for trip invite")
                # wait for invite card to disappear or participants to update
                await asyncio.sleep(1)
            except Exception as e:
                fail(f"Click Join failed: {e}")

            # Also accept the same trip from the second account (Legend/Mike)
            try:
                # Logout current Karel session
                try:
                    await page.get_by_role('button', name='Logout').click()
                except Exception:
                    try:
                        await page.locator("button:has-text('Logout')").first.click()
                    except Exception:
                        try:
                            await page.get_by_text('Logout').click()
                        except Exception:
                            pass

                # wait for login form
                for _ in range(40):
                    if await page.locator("input[formcontrolname='email']").count() > 0:
                        break
                    await asyncio.sleep(0.15)
                ok('Logged out (or returned to login)')

                # Login as second account (mikemails / Legend)
                await page.fill("input[formcontrolname='email']", "mikemails123456@gmail.com")
                await page.fill("input[formcontrolname='password']", "12345678")
                ok('Filled Legend/Mike credentials')
                await asyncio.sleep(1)
                await page.get_by_role('button', name='Sign In').click()

                # wait for login to complete
                signed2 = False
                for _ in range(60):
                    try:
                        if page.url.endswith('/trips') or await page.locator("mat-card:has-text('Trips')").count() > 0:
                            signed2 = True
                            break
                    except Exception:
                        pass
                    token = await page.evaluate("() => localStorage.getItem('authToken')")
                    if token:
                        signed2 = True
                        break
                    await asyncio.sleep(0.25)
                if signed2:
                    ok('Signed in as Legend/Mike')
                    await asyncio.sleep(5)
                else:
                    fail('Legend/Mike did not sign in')

                # open friends and click Join/Accept for any trip invites
                await page.goto('http://localhost:4200/friends')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                # Click any Join buttons present
                for _ in range(10):
                    btns = page.locator("button:has-text('Join')")
                    cnt = await btns.count()
                    if cnt == 0:
                        break
                    for i in range(cnt):
                        try:
                            b = btns.nth(i)
                            await b.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            await b.click()
                        except Exception:
                            continue
                    await asyncio.sleep(0.5)
                ok('Legend/Mike accepted trip invites (if any)')
            except Exception as e:
                fail(f'Legend/Mike accept flow failed: {e}')

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
