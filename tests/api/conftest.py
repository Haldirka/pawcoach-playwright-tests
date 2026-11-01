
import uuid

import pytest


@pytest.fixture
def api_user(playwright, base_url):
    context = playwright.request.new_context(base_url=base_url)

    try:
        email = f"api_{uuid.uuid4().hex}@example.com"
        password = f"Test_{uuid.uuid4().hex}!Aa1"

        register_response = context.post(
            "/api/auth/register",
            data={
                "email": email,
                "password": password,
                "confirm_password": password,
                "language": "en",
            },
        )

        assert register_response.status == 201, (
            f"Registration failed: {register_response.status}. "
            f"Response: {register_response.text()}"
        )

        login_response = context.post(
            "/api/auth/login",
            data={
                "email": email,
                "password": password,
                "language": "en",
            },
        )

        assert login_response.status == 200, (
            f"Login failed: {login_response.status}. "
            f"Response: {login_response.text()}"
        )

        yield context

    finally:
        context.dispose()
