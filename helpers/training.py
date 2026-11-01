
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError


def complete_training(page: Page):
    page.get_by_test_id("lesson-start").click()

    help_toggle = page.get_by_test_id("lesson-help-toggle")
    next_button = page.get_by_test_id("lesson-next")
    ready_button = page.get_by_test_id("practice-start")

    while True:
        # Check whether the current step offers help.
        if help_toggle.is_visible():
            try:
                help_toggle.click(timeout=2000)
            except PlaywrightTimeoutError:
                # Help is optional and may disappear during a UI update.
                pass

        # Stop when the final demonstration step is reached.
        if next_button.is_disabled():
            break

        try:
            next_button.click(timeout=3000)
        except PlaywrightTimeoutError:
            if next_button.is_disabled():
                break
            raise

    expect(next_button).to_be_disabled()
    expect(ready_button).to_be_enabled()

    # Start practice.
    ready_button.click()

    # Finish the session.
    page.get_by_test_id("session-finish").click()

    # Submit feedback.
    performance_slider = page.get_by_test_id("feedback-performance")
    difficulty_slider = page.get_by_test_id("feedback-difficulty")
    engagement_slider = page.get_by_test_id("feedback-engagement")

    performance_slider.nth(0).focus()
    performance_slider.nth(0).press("ArrowRight")
    performance_slider.nth(0).press("ArrowRight")

    difficulty_slider.nth(0).focus()
    difficulty_slider.nth(0).press("ArrowRight")
    difficulty_slider.nth(0).press("ArrowRight")

    engagement_slider.nth(0).focus()
    engagement_slider.nth(0).press("ArrowRight")

    page.get_by_test_id("feedback-submit").click()

    # Return home.
    page.get_by_test_id("link-home").click()
    expect(page.get_by_test_id("link-train")).to_be_visible()
