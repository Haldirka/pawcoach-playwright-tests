from dotenv import load_dotenv
from playwright.sync_api import Page, expect
import pytest
load_dotenv()


def test_login_fields_are_visible(page: Page):
    page.goto("/")

    email = page.get_by_label("Email")
    password = page.get_by_label("Password", exact=True)

    expect(email).to_be_visible()
    expect(password).to_be_visible()

@pytest.mark.parametrize(
    "transform",
    [
        pytest.param(lambda email: email, id="normal"),
        pytest.param(lambda email: email.upper(), id="uppercase"),
        pytest.param(lambda email: f"  {email}  ", id="spaces"),
    ],
)

def test_login_with_email_variations(page: Page, transform, credentials):
    email_input, password_input = credentials
    page.goto("/")

    test_email = transform(email_input)
    page.get_by_test_id("login-email").fill(test_email)
    page.get_by_test_id("login-password").fill(password_input)

    login_button = page.get_by_test_id("login-submit")
    expect(login_button).to_be_enabled(timeout=10000)
    login_button.click()

    expect(page.get_by_test_id("link-train")).to_be_visible()
    expect(page.get_by_test_id("login-email")).not_to_be_visible()