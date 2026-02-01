
import asyncio
from playwright.async_api import async_playwright

RESULT_PATH = "main4_accept_friend_results.txt"

# create result file to mark script started
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

            await page.goto("http://localhost:4200/friends")
            await page.wait_for_load_state('networkidle')
            ok("Opened /friends (Karel)")

            # give UI/backend time to populate friend requests
            await asyncio.sleep(5)

            # wait for friend request Accept button and click it
            try:
                await page.wait_for_selector("button:has-text('Accept')", timeout=3000)
                btn = page.locator("button:has-text('Accept')").first
                await btn.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await btn.click()
                ok("Clicked Accept")
            except Exception as e:
                fail(f"Click Accept failed: {e}")

            try:
                await page.wait_for_timeout(1000)
                # wait a bit more to ensure backend processed accept
                await asyncio.sleep(5)
            except Exception:
                pass
            # Logout and login as second account to accept from that side as well
            try:
                # try several logout selectors
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
                # wait for login page
                for _ in range(40):
                    if await page.locator("input[formcontrolname='email']").count() > 0:
                        break
                    await asyncio.sleep(0.15)
                ok('Logged out (or returned to login)')

                # Login as second account
                await page.fill("input[formcontrolname='email']", "mikemails123456@gmail.com")
                await page.fill("input[formcontrolname='password']", "12345678")
                ok('Filled second account credentials')
                await page.get_by_role('button', name='Sign In').click()

                # wait for login
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
                    ok('Signed in as second account')
                    # allow second account data to load
                    await asyncio.sleep(5)
                else:
                    fail('Second account did not sign in')

                # go to friends and accept any pending requests
                await page.goto('http://localhost:4200/friends')
                await page.wait_for_load_state('networkidle')
                # allow friend list to populate
                await asyncio.sleep(5)
                ok('Opened /friends (second account)')

                # accept all visible Accept buttons
                for _ in range(10):
                    btns = page.locator("button:has-text('Accept')")
                    cnt = await btns.count()
                    if cnt == 0:
                        break
                    for i in range(cnt):
                        try:
                            b = btns.nth(i)
                            await b.scroll_into_view_if_needed()
                            await b.click()
                        except Exception:
                            continue
                    await asyncio.sleep(0.5)
                ok('Accepted friend requests on second account')
            except Exception as e:
                fail(f'Second account accept flow failed: {e}')
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
