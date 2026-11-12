"""One-time LinkedIn login helper.

Opens a visible browser. Sign in to LinkedIn yourself (including any 2FA/CAPTCHA).
When you reach your feed, the session cookies are saved to auth/linkedin_state.json
and auto-apply reuses them. Your password is never seen or stored by this app.
The saved file lets anyone holding it act as you on LinkedIn: keep it private.
"""
import os
from playwright.sync_api import sync_playwright

STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth", "linkedin_state.json")


def main():
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto("https://www.linkedin.com/login")
        print("Sign in to LinkedIn in the browser window (you have 5 minutes)...")
        page.wait_for_url("**/feed/**", timeout=5 * 60 * 1000)
        context.storage_state(path=STATE_PATH)
        print(f"Saved session to {STATE_PATH}")
        browser.close()


if __name__ == "__main__":
    main()
