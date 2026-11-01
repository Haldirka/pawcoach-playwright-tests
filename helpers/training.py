
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError


def complete_training(page: Page):
    page.get_by_test_id("lesson-start").click()

    help_toggle = page.get_by_test_id("lesson-help-toggle")
    next_button = page.get_by_test_id("lesson-next")
    ready_button = page.get_by_test_id("practice-start")

    # Prevent an infinite loop if the UI stops progressing.
    visited_steps = set()

    while True:
        # Identify the current demonstration step.
        step_buttons = page.get_by_role("button", name="Step", exact=False)
        active_steps = step_buttons.filter(has=page.locator("[aria-pressed='true']"))

        # Stop when Next is disabled.
        if next_button.is_disabled():
            break

        # Open the optional help section, if available.
        if help_toggle.count() > 0 and help_toggle.is_visible():
            help_section = page.locator("details").filter(
                has=help_toggle
            )

            if help_section.count() > 0:
                if help_section.get_attribute("open") is None:
                    help_toggle.click()

                    # The help panel may disappear during React updates.
                    if help_section.count() > 0:
                        expect(help_section).to_have_attribute(
                            "open", "",
                            timeout=2000
                        )

        # Move to the next demonstration step.
        try:
            next_button.click(timeout=3000)
        except PlaywrightTimeoutError:
            if next_button.is_disabled():
                break
            raise

    # Verify the demonstration is complete.
    expect(next_button).to_be_disabled()
    expect(ready_button).to_be_enabled()

    # Start practice.
    ready_button.click()

    # Finish the session.
    page.get_by_test_id("session-finish").click()

    # Submit training feedback.
    performance_slider = page.get_by_test_id("feedback-performance")
    difficulty_slider = page.get_by_test_id("feedback-difficulty")
    engagement_slider = page.get_by_test_id("feedback-engagement")

    performance_slider.focus()
    performance_slider.press("ArrowRight")
    performance_slider.press("ArrowRight")

    difficulty_slider.focus()
    difficulty_slider.press("ArrowRight")
    difficulty_slider.press("ArrowRight")

    engagement_slider.focus()
    engagement_slider.press("ArrowRight")

    page.get_by_test_id("feedback-submit").click()

    # Return to the home page.
    page.get_by_test_id("link-home").click()
    expect(page.get_by_test_id("link-train")).to_be_visible()
