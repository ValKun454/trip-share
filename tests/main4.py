import asyncio
from playwright.async_api import async_playwright

RESULT_PATH = "main4_results.txt"


import asyncio
from playwright.async_api import async_playwright

RESULT_PATH = "main4_results.txt"


async def run():
    results = []

    def ok(msg):
        results.append("OK: " + msg)
        print("OK: " + msg)

    def fail(msg):
        results.append("FAIL: " + msg)
        print("FAIL: " + msg)

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False, slow_mo=150, args=["--start-fullscreen", "--start-maximized", "--kiosk"])
        context = await browser.new_context(viewport=None, no_viewport=True)
        page = await context.new_page()

        try:
            # 1) Login
            try:
                await page.goto("http://localhost:4200/login")
                ok("Opened /login")
            except Exception as e:
                fail(f"Open /login: {e}")

            try:
                await page.get_by_label("Email").fill("daniilsergej.mail@gmail.com")
                ok("Filled Email field")
            except Exception:
                try:
                    await page.fill("input[formcontrolname='email']", "daniilsergej.mail@gmail.com")
                    ok("Filled Email via selector")
                except Exception as e:
                    fail(f"Fill email failed: {e}")

            try:
                await page.get_by_label("Password").fill("Kami1234")
                ok("Filled Password field")
            except Exception:
                try:
                    await page.fill("input[formcontrolname='password']", "Kami1234")
                    ok("Filled Password via selector")
                except Exception as e:
                    fail(f"Fill password failed: {e}")
            try:
                await asyncio.sleep(1)
                await page.get_by_role("button", name="Sign In").click()
                ok("Clicked Sign In")
            except Exception as e:
                fail(f"Click Sign In failed: {e}")

            await page.wait_for_timeout(1000)

            # --- Add friend test: go to Friends page and add user id 30 ---
            try:
                await page.goto("http://localhost:4200/friends")
                ok("Opened /friends")
            except Exception as e:
                fail(f"Open /friends failed: {e}")

            try:
                await page.fill("input[formControlName='userId']", "30")
                ok("Filled Friend User ID = 30")
                await asyncio.sleep(1)
            except Exception as e:
                fail(f"Fill Friend User ID failed: {e}")

            try:
                # Click Add Friend button (mat-raised-button)
                    try:
                        await asyncio.sleep(1)
                        await page.get_by_role("button", name="Add Friend").click()
                    except Exception:
                        await page.get_by_text("Add Friend").click()
                    ok("Clicked Add Friend")
            except Exception as e:
                fail(f"Click Add Friend failed: {e}")

            await page.wait_for_timeout(1000)

            # 2) Open New Trip
            try:
                await page.get_by_role("button", name="New Trip").click()
                ok("Opened New Trip panel")
            except Exception:
                try:
                    await page.get_by_text("New Trip").click()
                    ok("Opened New Trip panel (text click)")
                except Exception as e:
                    fail(f"Open New Trip failed: {e}")

            await page.wait_for_timeout(500)

            # 3) Fill trip fields
            try:
                await page.fill("input[formcontrolname='name']", "E2E Trip")
                ok("Filled Trip name")
            except Exception as e:
                fail(f"Fill Trip name failed: {e}")

            try:
                await page.fill("textarea[formcontrolname='description']", "Created by automated test")
                ok("Filled Description")
            except Exception as e:
                fail(f"Fill Description failed: {e}")

            try:
                # use locale format as shown in UI (dd/mm/YYYY)
                await page.fill("input[formcontrolname='startDate']", "20/12/2025")
                ok("Filled Start date")
            except Exception as e:
                fail(f"Fill Start date failed: {e}")

            try:
                await page.fill("input[formcontrolname='endDate']", "25/12/2025")
                ok("Filled End date")
            except Exception as e:
                fail(f"Fill End date failed: {e}")

            # 4) Open friends dropdown and select Karel only
            try:
                # open select (mat-select)
                await page.get_by_label("SELECT FRIENDS").click()
                ok("Opened Select Friends dropdown")
                # wait for mat-option with text 'Karel' and click it
                try:
                    opt = page.locator("mat-option", has_text="Karel").first
                    await opt.wait_for(timeout=3000)
                    await opt.click()
                    ok("Selected friend Karel")
                except Exception:
                    # fallback: click by visible text
                    await page.get_by_text("Karel").click()
                    ok("Selected friend Karel (fallback)")
                # close dropdown if still open
                try:
                    await page.keyboard.press('Escape')
                except Exception:
                    pass
            except Exception as e:
                fail(f"Selecting Karel failed: {e}")

            # 5) Create trip — wait for enabled submit button then click
            try:
                submit = page.locator("button[type='submit']")
                # wait up to 7s for it to become enabled
                elapsed = 0.0
                interval = 0.2
                max_time = 7.0
                clicked = False
                while elapsed < max_time:
                    try:
                        if await submit.is_enabled():
                            await submit.click()
                            ok("Clicked Create (submit)")
                            clicked = True
                            break
                    except Exception:
                        pass
                    await asyncio.sleep(interval)
                    elapsed += interval
                if not clicked:
                    # fallback to role/text click
                    try:
                        await page.get_by_role("button", name="Create").click()
                        ok("Clicked Create (fallback)")
                    except Exception as e:
                        fail(f"Click Create failed: {e}")
            except Exception as e:
                fail(f"Click Create failed: {e}")

            await page.wait_for_timeout(1000)

        finally:
            await context.close()
            await browser.close()

    # write results
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        for r in results:
            f.write(r + "\n")

    print("Results written to", RESULT_PATH)


if __name__ == '__main__':
    asyncio.run(run())

