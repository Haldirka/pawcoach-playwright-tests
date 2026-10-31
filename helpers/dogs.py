from urllib.parse import urlsplit

from playwright.sync_api import Page, expect

from helpers.checks import current_account, owned_dogs


def create_dog(
    page: Page, dog_name: str, expected_account_id: int | None = None
) -> dict:
    before = current_account(page, "Immediately before dog creation")
    if expected_account_id is not None:
        assert before["id"] == expected_account_id, (
            "Stopped before saving: browser is no longer the registered account. "
            f"Expected {expected_account_id}, got {before['id']}."
        )

    page.get_by_test_id("dog-name").fill(dog_name)
    page.get_by_test_id("dog-breed").select_option("Labrador")
    page.get_by_test_id("dog-age").select_option("Adult")
    page.get_by_test_id("dog-experience").select_option("Brand new")

    save_button = page.get_by_test_id("dog-save")
    expect(save_button).to_be_enabled()
    with page.expect_response(
        lambda response: urlsplit(response.url).path == "/api/dogs"
        and response.request.method == "POST"
    ) as result:
        save_button.click()

    response = result.value
    sent_account = response.request.headers.get("x-pawcoach-account")
    print(
        f"Dog creation: HTTP {response.status}, "
        f"X-PawCoach-Account={sent_account!r}, expected={before['id']}"
    )
    assert response.status == 201, (
        f"Dog creation failed: HTTP {response.status}, body={response.text()}."
    )
    assert sent_account == str(before["id"]), (
        "The browser did not send the expected v1.0.3 account guard. "
        "Health version alone does not verify the frontend files. "
        "Check frontend/dist was replaced, then reload all PawCoach tabs."
    )
    dog = response.json()
    expect(page.get_by_test_id("dog-name")).not_to_be_visible()
    after = current_account(page, "Immediately after dog creation")
    assert after["id"] == before["id"], "Account changed during dog creation."
    assert any(item["id"] == dog["id"] for item in owned_dogs(page)), (
        "The created dog is not in the registered account's dog list."
    )
    print(f"Created dog_id={dog['id']} under verified account_id={after['id']}")
    return dog
