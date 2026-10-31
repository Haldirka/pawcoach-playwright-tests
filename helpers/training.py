from playwright.sync_api import Page, expect


def complete_training(page: Page):
    page.get_by_test_id("lesson-start").click()

    help_toggle = page.get_by_test_id("lesson-help-toggle")
    next_button = page.get_by_test_id("lesson-next")
    ready_button = page.get_by_test_id("practice-start")

    while True:
        if help_toggle.count() > 0:
            help_section = page.locator("details").filter(
                has=help_toggle
            )

            if help_section.count() > 0:
                if help_section.get_attribute("open") is None:
                    help_toggle.click()

                if help_section.count() > 0:
                    expect(help_section).to_have_attribute("open", "")

        if next_button.is_disabled():
            break

        try:
            next_button.click(timeout=2000)
        except Exception:
            if next_button.is_disabled():
                break
            raise

    expect(next_button).to_be_disabled()
    expect(ready_button).to_be_enabled()
    ready_button.click()
    page.get_by_test_id("session-finish").click()

    permormance_slide = page.get_by_test_id("feedback-performance")
    difficulty_slide = page.get_by_test_id("feedback-difficulty")
    engagement_slide = page.get_by_test_id("feedback-engagement")

    permormance_slide.nth(0).focus()
    permormance_slide.nth(0).press("ArrowRight")
    permormance_slide.nth(0).press("ArrowRight")

    difficulty_slide.nth(0).focus()
    difficulty_slide.nth(0).press("ArrowRight")
    difficulty_slide.nth(0).press("ArrowRight")

    engagement_slide.nth(0).focus()
    engagement_slide.nth(0).press("ArrowRight")

    page.get_by_test_id("feedback-submit").click()

    page.get_by_test_id("link-home").click()

    expect(page.get_by_test_id("link-train")).to_be_visible()