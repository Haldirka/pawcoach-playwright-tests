import os
import uuid
from urllib.parse import urlsplit

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

from helpers.checks import api_url, assert_account, assert_anonymous, owned_dogs
from helpers.dogs import create_dog

load_dotenv()


@pytest.fixture
def credentials():
    email = os.getenv("PAWCOACH_EMAIL")
    password = os.getenv("PAWCOACH_PASSWORD")
    assert email, "PAWCOACH_EMAIL is missing"
    assert password, "PAWCOACH_PASSWORD is missing"
    return email, password


@pytest.fixture
def new_user():
    return {
        "email": f"pawcoach_test_{uuid.uuid4().hex[:10]}@example.com",
        "password": "TestPassword123!",
    }


@pytest.fixture
def register_user(page: Page, new_user):
    page.goto("/")
    health = page.request.get(api_url(page, "/api/health"))
    assert health.status == 200, "PawCoach API is not available."
    print(f"App version: {health.json().get('version')}")
    assert_anonymous(page)
    page.get_by_test_id("header-language").select_option("en")
    page.get_by_test_id("auth-switch").click()
    expect(page.get_by_test_id("registration-form")).to_be_visible()
    page.get_by_test_id("login-email").fill(new_user["email"])
    page.get_by_test_id("login-password").fill(new_user["password"])
    page.get_by_test_id("register-confirm-password").fill(new_user["password"])

    with page.expect_response(
        lambda response: urlsplit(response.url).path == "/api/auth/register"
        and response.request.method == "POST"
    ) as result:
        page.get_by_test_id("login-submit").click()

    response = result.value
    assert response.status == 201, f"Registration failed: HTTP {response.status}."
    registered = response.json()
    assert registered["email"].casefold() == new_user["email"].casefold()
    new_user["account_id"] = registered["id"]
    print(f"Registration response: new account_id={registered['id']}")
    expect(page.get_by_test_id("dog-name")).to_be_visible()
    assert_account(page, new_user, "After registration")
    assert owned_dogs(page) == [], "A newly registered account already has dogs."
    return new_user


@pytest.fixture
def login(page: Page, credentials):
    page.goto("/login")
    email, password = credentials
    page.get_by_test_id("login-email").fill(email)
    page.get_by_test_id("login-password").fill(password)
    button = page.get_by_test_id("login-submit")
    expect(button).to_be_enabled(timeout=10000)
    with page.expect_response(
        lambda response: urlsplit(response.url).path == "/api/auth/login"
        and response.request.method == "POST"
    ) as result:
        button.click()
    assert result.value.status == 200, "Login failed."
    expect(page.get_by_test_id("login-email")).not_to_be_visible()
    assert_account(page, {"email": email}, "After existing-account login")


@pytest.fixture
def user_with_dog(page: Page, register_user):
    dog_name = f"Buddy_{uuid.uuid4().hex[:8]}"
    assert_account(page, register_user, "Before create_dog helper")
    dog = create_dog(page, dog_name, expected_account_id=register_user["account_id"])
    register_user["dog_id"] = dog["id"]
    page.get_by_test_id("link-dogs").click()
    expect(page.get_by_role("region", name=dog_name, exact=True)).to_be_visible()
    assert_account(page, register_user, "After opening the dog list")
    return dog_name
