from playwright.sync_api import Page, expect

def test_login_fields_are_visible(page: Page):
    page.goto("http://localhost:8501/")

    email = page.get_by_label("Email")
    password = page.get_by_label("Password", exact=True)

    expect(email).to_be_visible()
    expect(password).to_be_visible()
