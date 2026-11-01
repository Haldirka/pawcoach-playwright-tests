import uuid

import pytest
from playwright.sync_api import Playwright

def test_login_with_valid_credentials(
    playwright,
    credentials,
    base_url
):
    email, password = credentials

    request = playwright.request.new_context(base_url=base_url)

    try:
        response = request.post(
            "/api/auth/login",
            data={
                "email": email,
                "password": password,
            },
        )

        assert response.status == 200, (
            f"Expected 200, got {response.status}. "
            f"Response: {response.text()}"
        )

        body = response.json()
        assert isinstance(body, dict)
        assert body["email"].casefold() == email.casefold()
        assert body.get("id") is not None

        me = request.get("/api/auth/me")
        assert me.status == 200
        assert me.json()["id"] == body["id"]

    finally:
        request.dispose()

@pytest.mark.parametrize(
    "scenario",
    [
        "wrong_password",
        "nonexistent_email",
        "empty_password",
        "empty_email",
        "both_empty",
    ],
)
def test_login_with_invalid_credentials(
    playwright: Playwright,
    credentials,
    base_url,
    scenario,
):
    email, password = credentials

    invalid_credentials = {
        "wrong_password": {
            "email": email,
            "password": "DefinitelyWrongPassword_123!",
        },
        "nonexistent_email": {
            "email": f"nonexistent_{uuid.uuid4().hex}@example.com",
            "password": password,
        },
        "empty_password": {
            "email": email,
            "password": "",
        },
        "empty_email": {
            "email": "",
            "password": password,
        },
        "both_empty": {
            "email": "",
            "password": "",
        },
    }

    request = playwright.request.new_context(base_url=base_url)

    try:
        response = request.post(
            "/api/auth/login",
            data={
                **invalid_credentials[scenario],
                "language": "en",
            },
        )

        expected_statuses = (401,) if scenario in (
            "wrong_password", "nonexistent_email"
        ) else (401, 422)
        assert response.status in expected_statuses, (
            f"Scenario '{scenario}' returned unexpected HTTP {response.status}. "
            f"Response: {response.text()}"
        )

        body = response.json()

        assert "detail" in body, (
            f"Scenario '{scenario}' returned no error details"
        )

        if response.status == 401:
            assert body["detail"]["code"] == "invalid_credentials"

        # A failed login must not establish an authenticated session.
        me = request.get("/api/auth/me")
        assert me.status == 401, (
            f"Rejected login unexpectedly authenticated a session: HTTP {me.status}"
        )

    finally:
        request.dispose()
