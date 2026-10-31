"""Read-only identity checks using the browser page's own cookie context."""
from urllib.parse import urljoin

from playwright.sync_api import Page


def api_url(page: Page, path: str) -> str:
    return urljoin(page.url, path)


def current_account(page: Page, stage: str) -> dict:
    response = page.request.get(api_url(page, "/api/auth/me"))
    assert response.status == 200, (
        f"{stage}: expected a signed-in browser, got HTTP {response.status}."
    )
    account = response.json()
    print(f"{stage}: account_id={account['id']}, email={account['email']}")
    return account


def assert_account(page: Page, expected: dict, stage: str) -> dict:
    account = current_account(page, stage)
    assert account["email"].casefold() == expected["email"].strip().casefold(), (
        f"{stage}: wrong browser account. Expected {expected['email']}, "
        f"got {account['email']} (id={account['id']})."
    )
    if "account_id" in expected:
        assert account["id"] == expected["account_id"], (
            f"{stage}: account ID changed from {expected['account_id']} "
            f"to {account['id']}."
        )
    return account


def assert_anonymous(page: Page) -> None:
    response = page.request.get(api_url(page, "/api/auth/me"))
    if response.status == 200:
        account = response.json()
        raise AssertionError(
            "Registration started with an already authenticated page: "
            f"account_id={account['id']}, email={account['email']}. "
            "Check autouse fixtures, storage_state, browser_context_args "
            "and any custom page/context fixture. No dog was created."
        )
    assert response.status == 401, (
        f"Expected anonymous HTTP 401 before registration, got {response.status}."
    )


def owned_dogs(page: Page) -> list[dict]:
    response = page.request.get(api_url(page, "/api/dogs"))
    assert response.status == 200, f"Dog list failed: HTTP {response.status}."
    return response.json()
