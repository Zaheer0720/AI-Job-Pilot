import asyncio
import os
import re
import time
import random
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser
from models.schemas import JobListing, ResumeProfile, ApplicationResult
from services.gemini_service import fill_form_field, generate_cover_letter


SCREENSHOTS_DIR = "screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Saved LinkedIn session created by login.bat / linkedin_login.py
LINKEDIN_STATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "auth", "linkedin_state.json")

LOGIN_REQUIRED_MSG = (
    "LinkedIn login required. Run login.bat once to sign in, then try again."
)


async def linkedin_logged_out(page: Page) -> bool:
    """True if the LinkedIn page is showing the logged-out/auth-wall view."""
    if "authwall" in page.url or "/login" in page.url or "/signup" in page.url:
        return True
    # Logged in = we hold the li_at session cookie and the sign-up modal isn't shown
    cookies = await page.context.cookies("https://www.linkedin.com")
    if not any(c["name"] == "li_at" for c in cookies):
        return True
    return await page.locator(".sign-up-modal__outlet, [data-modal='job-details-subnav-apply-modal']").count() > 0


def login_required_result(job: JobListing) -> ApplicationResult:
    return ApplicationResult(
        job_id=job.id, job_title=job.title, company=job.company,
        portal=job.portal, url=job.url, status="requires_manual",
        message=LOGIN_REQUIRED_MSG,
    )


async def human_delay(min_ms: int = 500, max_ms: int = 2000):
    """Add a human-like delay to avoid bot detection."""
    delay = random.uniform(min_ms / 1000, max_ms / 1000)
    await asyncio.sleep(delay)


async def human_type(page: Page, field, text: str):
    """Type text into the given element handle with human-like speed and delays."""
    await field.click()
    await human_delay(200, 500)
    for char in text:
        await page.keyboard.type(char, delay=random.uniform(30, 120))


async def ask_gemini(func, *args, **kwargs):
    """Run a blocking Gemini call in a worker thread so the event loop stays free."""
    return await asyncio.to_thread(func, *args, **kwargs)


async def fill_input_field(page: Page, field, profile: ResumeProfile) -> bool:
    """Intelligently fill a single form input using Gemini."""
    try:
        # Get field metadata
        field_type = await field.get_attribute("type") or "text"
        field_name = await field.get_attribute("name") or ""
        field_id = await field.get_attribute("id") or ""
        placeholder = await field.get_attribute("placeholder") or ""
        field_label = field_name or field_id or placeholder or "unknown field"

        # Skip hidden, file, submit, checkbox fields (handle separately)
        if field_type in ["hidden", "file", "submit", "button", "image", "reset"]:
            return False

        # Check if field is already filled
        current_value = await field.input_value()
        if current_value and len(current_value) > 2:
            return False  # Already has a value

        if field_type == "email":
            value = profile.email
        elif field_type == "tel":
            value = profile.phone
        elif field_type in ["checkbox", "radio"]:
            return False  # Never tick consent/eligibility boxes automatically
        else:
            # Use Gemini to determine what to fill (returns "" when unsure)
            value = await ask_gemini(
                fill_form_field,
                field_label=field_label,
                field_type=field_type,
                profile=profile,
                context=f"placeholder: {placeholder}"
            )

        if value and value.lower() not in ["none", "n/a", "null", ""]:
            await field.fill("")
            await human_type(page, field, value)
            await human_delay(100, 300)
            return True

    except Exception as e:
        print(f"Error filling field: {e}")

    return False


async def handle_linkedin_easy_apply(
    page: Page,
    job: JobListing,
    profile: ResumeProfile,
    resume_path: str,
    auto_submit: bool = False
) -> ApplicationResult:
    """Handle LinkedIn Easy Apply flow."""
    screenshot_path = ""
    try:
        await page.goto(job.url, wait_until="load", timeout=120000)
        await human_delay(1000, 2000)

        if await linkedin_logged_out(page):
            return login_required_result(job)

        # Click Easy Apply button
        easy_apply_btn = page.locator("button:has-text('Easy Apply'), .jobs-apply-button")
        try:
            # The page is dynamic: give the apply button up to 60s to render
            await easy_apply_btn.first.wait_for(state="visible", timeout=60000)
        except Exception:
            pass
        if await easy_apply_btn.count() == 0:
            return ApplicationResult(
                job_id=job.id,
                job_title=job.title,
                company=job.company,
                portal=job.portal,
                url=job.url,
                status="requires_manual",
                message="No Easy Apply button found. Please apply manually."
            )

        await easy_apply_btn.first.click()
        await human_delay(1500, 3000)

        # Multi-step form handling
        step = 0
        max_steps = 10

        while step < max_steps:
            step += 1

            # Fill all visible text inputs
            inputs = await page.locator("input:visible:not([type='hidden']):not([type='submit'])").all()
            for inp in inputs:
                await fill_input_field(page, inp, profile)

            # Fill textareas (cover letter, etc.)
            textareas = await page.locator("textarea:visible").all()
            for ta in textareas:
                try:
                    current = await ta.input_value()
                    if not current or len(current) < 10:
                        label_text = await ta.get_attribute("aria-label") or "cover letter"
                        if "cover" in label_text.lower() or "letter" in label_text.lower():
                            cover_letter = await ask_gemini(generate_cover_letter, profile, job)
                            await ta.fill(cover_letter)
                        else:
                            value = await ask_gemini(fill_form_field, label_text, "textarea", profile)
                            if value:
                                await ta.fill(value)
                        await human_delay(300, 800)
                except Exception as e:
                    print(f"Error filling textarea: {e}")

            # Handle resume upload
            file_inputs = await page.locator("input[type='file']").all()
            if file_inputs and resume_path and os.path.exists(resume_path):
                for fi in file_inputs:
                    try:
                        await fi.set_input_files(resume_path)
                        await human_delay(1000, 2000)
                        break
                    except Exception as e:
                        print(f"Error uploading resume: {e}")

            # Handle select dropdowns
            selects = await page.locator("select:visible").all()
            for sel in selects:
                try:
                    sel_name = await sel.get_attribute("name") or await sel.get_attribute("id") or "dropdown"
                    options = await sel.locator("option").all()
                    option_texts = [await o.text_content() for o in options if await o.text_content()]
                    if option_texts:
                        value = await ask_gemini(fill_form_field, sel_name, "select", profile, f"options: {option_texts}")
                        # Find matching option (empty value = Gemini unsure, leave unselected)
                        if value:
                            for opt_text in option_texts:
                                if value.lower() in opt_text.lower():
                                    await sel.select_option(label=opt_text)
                                    break
                except Exception as e:
                    print(f"Error filling select: {e}")

            # Screenshot current state
            screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{job.id}_step{step}.png")
            await page.screenshot(path=screenshot_path, full_page=False)

            # Look for Next/Continue button
            next_btn = page.locator("button:has-text('Next'), button:has-text('Continue'), button:has-text('Review')")
            submit_btn = page.locator("button[aria-label='Submit application'], button:has-text('Submit application')")

            if await submit_btn.count() > 0:
                if auto_submit:
                    # Safety: never submit while the form shows validation errors
                    if await page.locator(".artdeco-inline-feedback--error:visible").count() > 0:
                        return ApplicationResult(
                            job_id=job.id,
                            job_title=job.title,
                            company=job.company,
                            portal=job.portal,
                            url=job.url,
                            status="requires_manual",
                            message="Form has unanswered or invalid required fields. Not submitted; please complete manually.",
                            screenshot_path=screenshot_path
                        )
                    await submit_btn.first.click()
                    await human_delay(2000, 4000)
                    # Only report success if LinkedIn confirms it
                    confirmed = await page.get_by_text(
                        re.compile(r"application was sent|application submitted", re.I)
                    ).count() > 0
                    screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{job.id}_submitted.png")
                    await page.screenshot(path=screenshot_path, full_page=False)
                    return ApplicationResult(
                        job_id=job.id,
                        job_title=job.title,
                        company=job.company,
                        portal=job.portal,
                        url=job.url,
                        status="applied" if confirmed else "requires_manual",
                        message=(
                            "Application submitted via LinkedIn Easy Apply (confirmation seen)."
                            if confirmed else
                            "Submit was clicked but no confirmation was detected. Please verify on LinkedIn."
                        ),
                        screenshot_path=screenshot_path
                    )
                else:
                    return ApplicationResult(
                        job_id=job.id,
                        job_title=job.title,
                        company=job.company,
                        portal=job.portal,
                        url=job.url,
                        status="requires_manual",
                        message="Application form filled. Please review and submit manually. Auto-submit is disabled for safety.",
                        screenshot_path=screenshot_path
                    )
            elif await next_btn.count() > 0:
                await next_btn.first.click()
                await human_delay(1500, 3000)
            else:
                break

        return ApplicationResult(
            job_id=job.id,
            job_title=job.title,
            company=job.company,
            portal=job.portal,
            url=job.url,
            status="requires_manual",
            message="Reached form limit. Please complete manually.",
            screenshot_path=screenshot_path
        )

    except Exception as e:
        return ApplicationResult(
            job_id=job.id,
            job_title=job.title,
            company=job.company,
            portal=job.portal,
            url=job.url,
            status="failed",
            message=f"Error during application: {type(e).__name__}: {e}",
            screenshot_path=screenshot_path
        )


async def apply_to_job(
    job: JobListing,
    profile: ResumeProfile,
    resume_path: str,
    headless: bool = True,
    auto_submit: bool = False
) -> ApplicationResult:
    """Apply to a single job using Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context_kwargs = dict(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        if job.portal == "linkedin" and os.path.exists(LINKEDIN_STATE):
            context_kwargs["storage_state"] = LINKEDIN_STATE  # start already signed in
        context = await browser.new_context(**context_kwargs)
        page = await context.new_page()

        # Remove automation detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)

        try:
            # jobspy rarely flags LinkedIn Easy Apply, so always try the LinkedIn flow;
            # it falls back to "requires manual" if there is no Easy Apply button.
            if job.portal == "linkedin":
                result = await handle_linkedin_easy_apply(page, job, profile, resume_path, auto_submit)
            else:
                # Generic application handler for other portals
                result = await handle_generic_apply(page, job, profile, resume_path, auto_submit)
        finally:
            await browser.close()

        return result


async def handle_generic_apply(
    page: Page,
    job: JobListing,
    profile: ResumeProfile,
    resume_path: str,
    auto_submit: bool = False
) -> ApplicationResult:
    """Generic handler for job portals with application forms."""
    screenshot_path = ""
    try:
        await page.goto(job.url, wait_until="load", timeout=120000)
        await human_delay(1500, 3000)

        # Look for Apply button
        apply_btn = page.locator(
            "button:has-text('Apply'), a:has-text('Apply Now'), button:has-text('Apply Now'), "
            "a:has-text('Apply'), button:has-text('Quick Apply')"
        )

        if await apply_btn.count() > 0:
            await apply_btn.first.click()
            await human_delay(2000, 4000)

            # Fill all form fields
            inputs = await page.locator("input:visible:not([type='hidden'])").all()
            for inp in inputs:
                await fill_input_field(page, inp, profile)

            # Upload resume
            file_inputs = await page.locator("input[type='file']").all()
            if file_inputs and resume_path and os.path.exists(resume_path):
                await file_inputs[0].set_input_files(resume_path)
                await human_delay(1000, 2000)

            screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{job.id}_filled.png")
            await page.screenshot(path=screenshot_path, full_page=False)

            return ApplicationResult(
                job_id=job.id,
                job_title=job.title,
                company=job.company,
                portal=job.portal,
                url=job.url,
                status="requires_manual",
                message=f"Form partially filled. Please review and submit at: {job.url}",
                screenshot_path=screenshot_path
            )
        else:
            return ApplicationResult(
                job_id=job.id,
                job_title=job.title,
                company=job.company,
                portal=job.portal,
                url=job.url,
                status="requires_manual",
                message="Apply button not found. Please apply manually.",
            )
    except Exception as e:
        return ApplicationResult(
            job_id=job.id,
            job_title=job.title,
            company=job.company,
            portal=job.portal,
            url=job.url,
            status="failed",
            message=f"Application error: {type(e).__name__}: {e}",
            screenshot_path=screenshot_path
        )


async def apply_to_multiple_jobs(
    jobs: List[JobListing],
    profile: ResumeProfile,
    resume_path: str,
    headless: bool = True,
    auto_submit: bool = False,
    results: Optional[List[ApplicationResult]] = None,
) -> List[ApplicationResult]:
    """Apply to multiple jobs sequentially with delays.

    Pass a list as `results` to have each result appended as soon as it is ready
    (used for progress polling).
    """
    if results is None:
        results = []
    for i, job in enumerate(jobs):
        try:
            result = await apply_to_job(job, profile, resume_path, headless, auto_submit)
        except Exception as e:
            result = ApplicationResult(
                job_id=job.id, job_title=job.title, company=job.company,
                portal=job.portal, url=job.url, status="failed",
                message=f"Application error: {type(e).__name__}: {e}",
            )
        results.append(result)
        if i == len(jobs) - 1:
            break
        # Polite delay between applications
        await asyncio.sleep(random.uniform(5, 15))
    return results
