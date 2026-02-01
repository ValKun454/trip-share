import asyncio
from playwright.async_api import async_playwright

RESULT_PATH = "main4_add_friend_results.txt"

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
            await asyncio.sleep(1)
            ok("Filled credentials")
            # submit login and wait for navigation or authToken in localStorage
            await page.get_by_role("button", name="Sign In").click()
            signed = False
            try:
                # first wait briefly for a navigation to /trips
                try:
                    await page.wait_for_url("**/trips", timeout=8000)
                    ok("Signed in")
                    signed = True
                except Exception:
                    # if navigation didn't happen, poll localStorage for authToken
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

            await page.goto("http://localhost:4200/friends")
            await page.wait_for_load_state('networkidle')
            ok("Opened /friends")
            # allow frontend to process and load friends UI
            await asyncio.sleep(5)

            # wait for Friend User ID input to appear and fill by label
            await page.get_by_label("Friend User ID").wait_for(timeout=3000)
            await page.get_by_label("Friend User ID").fill("30")
            await asyncio.sleep(1)
            ok("Filled Friend User ID = 30")

            try:
                await page.get_by_role("button", name="Add Friend").click()
            except Exception:
                await page.get_by_text("Add Friend").click()
            ok("Clicked Add Friend")

            # give backend/frontend time to process the add-friend request
            await asyncio.sleep(5)

            # wait for success message or for the friends list to update
            try:
                await page.wait_for_selector("div.success-message", timeout=3000)
                ok("Friend request UI success shown")
            except Exception:
                # fallback: wait a bit for backend to process
                await page.wait_for_timeout(2000)
            # Also add friend with ID 19 (automated additional invite)
            # wait a bit before next invite to let the UI settle
            await asyncio.sleep(1)
            try:
                await page.get_by_label("Friend User ID").fill("19")
                await asyncio.sleep(1)
                ok("Filled Friend User ID = 19")
                try:
                    await page.get_by_role("button", name="Add Friend").click()
                except Exception:
                    await page.get_by_text("Add Friend").click()
                ok("Clicked Add Friend for 19")
                try:
                    await page.wait_for_selector("div.success-message", timeout=3000)
                    ok("Friend request UI success shown for 19")
                except Exception:
                    await page.wait_for_timeout(1500)
            except Exception as e:
                fail(f"Add friend 19 failed: {e}")

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
