# from urllib.parse import urlsplit
#
# from playwright.sync_api import Page, expect
#
# from helpers.checks import assert_account, owned_dogs
#
#
# def test_dog_editing_with_account_checks(page: Page, user_with_dog, register_user):
#     dog_name = user_with_dog
#     updated_name = f"{dog_name}_edited"
#     assert_account(page, register_user, "Before editing")
#     card = page.get_by_role("region", name=dog_name, exact=True)
#     card.get_by_test_id("dog-options").click()
#     card.get_by_test_id("dog-edit").click()
#     page.get_by_test_id("dog-name").fill(updated_name)
#     page.get_by_test_id("dog-breed").select_option("Husky")
#     page.get_by_test_id("dog-age").select_option("Puppy")
#     page.get_by_test_id("dog-experience").select_option("Experienced")
#     with page.expect_response(
#         lambda response: urlsplit(response.url).path == f"/api/dogs/{register_user['dog_id']}"
#         and response.request.method == "PATCH"
#     ) as result:
#         page.get_by_test_id("dog-save").click()
#     assert result.value.status == 200, "Dog editing failed."
#     page.get_by_test_id("link-dogs").click()
#     card = page.get_by_role("region", name=updated_name, exact=True)
#     expect(card).to_have_count(1)
#     expect(card.get_by_text(updated_name, exact=True)).to_be_visible()
#     expect(card.get_by_text("Husky · Puppy", exact=True)).to_be_visible()
#     assert_account(page, register_user, "After editing")
#     saved = next(d for d in owned_dogs(page) if d["id"] == register_user["dog_id"])
#     assert saved["name"] == updated_name
#     assert saved["breed"] == "Husky"
#     assert saved["age_group"] == "Puppy"
#     assert saved["training_level"] == "Experienced"
#
#
# def test_new_dog_is_not_in_existing_account(
#     page: Page, user_with_dog, register_user, credentials
# ):
#     dog_name = user_with_dog
#     new_id = register_user["account_id"]
#     dog_id = register_user["dog_id"]
#     assert_account(page, register_user, "Before signing out of test account")
#     page.goto("/account")
#     page.get_by_test_id("logout").click()
#     expect(page.get_by_test_id("login-form")).to_be_visible()
#     email, password = credentials
#     assert email.strip().casefold() != register_user["email"].casefold()
#     page.get_by_test_id("login-email").fill(email)
#     page.get_by_test_id("login-password").fill(password)
#     with page.expect_response(
#         lambda response: urlsplit(response.url).path == "/api/auth/login"
#         and response.request.method == "POST"
#     ) as result:
#         page.get_by_test_id("login-submit").click()
#     assert result.value.status == 200, "Existing-account login failed."
#     expect(page.get_by_test_id("login-form")).not_to_be_visible()
#     account = assert_account(page, {"email": email}, "Existing account after logout/login")
#     assert account["id"] != new_id, "Both logins resolved to the same account ID."
#     dogs = owned_dogs(page)
#     print(f"Existing account_id={account['id']}; dog_ids={[d['id'] for d in dogs]}")
#     assert all(d["id"] != dog_id for d in dogs), (
#         f"SERVER OWNERSHIP FAILURE: test dog_id={dog_id}, registered under "
#         f"account_id={new_id}, is listed for existing account_id={account['id']}."
#     )
#     page.goto("/dogs")
#     expect(page.get_by_role("region", name=dog_name, exact=True)).to_have_count(0)
