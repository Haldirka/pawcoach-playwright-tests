from dotenv import load_dotenv
from playwright.sync_api import Page, expect
import pytest
import uuid
load_dotenv()

def test_registration(page: Page, new_user):
    page.goto("/")

    page.get_by_test_id("auth-switch").click()
    expect(page.get_by_test_id("register-confirm-password")).to_be_visible()

    page.get_by_test_id("login-email").fill(new_user["email"])
    page.get_by_test_id("login-password").fill(new_user["password"])
    page.get_by_test_id("register-confirm-password").fill(new_user["password"])

    expect(page.get_by_test_id("login-submit")).to_be_enabled()
    page.get_by_test_id("login-submit").click()

    expect(page.get_by_test_id("dog-name")).to_be_visible()
    expect(page.get_by_test_id("login-email")).not_to_be_visible()

