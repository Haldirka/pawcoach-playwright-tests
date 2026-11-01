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
            "email": "nonexistent_account_987654@example.com",
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

        assert response.status in (401, 422), (
            f"Scenario '{scenario}' returned "
            f"unexpected HTTP {response.status}"
        )

        body = response.json()

        assert "detail" in body, (
            f"Scenario '{scenario}' returned no error details"
        )

        if response.status == 401:
            assert body["detail"]["code"] == "invalid_credentials"

    finally:
        request.dispose()
