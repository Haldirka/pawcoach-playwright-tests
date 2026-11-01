from helpers.dogs import create_dog
from playwright.sync_api import Page, expect
import uuid

def test_dog_creation_with_new_user(page: Page, register_user):
    create_dog(page, "Buddy")

    page.get_by_test_id("link-dogs").click()
    expect(page.get_by_text("Buddy", exact=True)).to_be_visible()

def test_dog_creation_with_existing_dogs(page: Page, user_with_dog):
    existing_dog_name = user_with_dog

    page.get_by_test_id("link-dogs-new").click()

    dog_name = f"Buddy_{uuid.uuid4().hex[:8]}"
    page.get_by_test_id("dog-name").fill(dog_name)
    page.get_by_test_id("dog-breed").select_option("Labrador")
    page.get_by_test_id("dog-age").select_option("Adult")
    page.get_by_test_id("dog-experience").select_option("Brand new")
    page.get_by_test_id("dog-photo").set_input_files(
        "tests/assets/dog.png"
    )

    save_button = page.get_by_test_id("dog-save")
    expect(save_button).to_be_enabled()
    save_button.click()

    page.get_by_test_id("link-dogs").click()
    expect(
        page.get_by_role("region", name=existing_dog_name, exact=True)
    ).to_be_visible()
    expect(
        page.get_by_role("region", name=dog_name, exact=True)
    ).to_be_visible()

def test_dog_deletion(page: Page, user_with_dog):
    dog_name = user_with_dog

    dog_card = page.locator(
        '[data-testid^="dog-card-"]'
    ).filter(has_text=dog_name)

    expect(dog_card).to_have_count(1)

    dog_card.locator('[data-testid^="dog-options-"]').click()
    dog_card.locator('[data-testid^="dog-delete-"]').click()
    page.get_by_test_id("dog-delete-confirm").click()

    expect(dog_card).to_have_count(0)

    page.reload()

    expect(dog_card).to_have_count(0)

def test_dog_editing(page: Page, user_with_dog):
    dog_name = user_with_dog
    updated_name = f"{dog_name}_edited"

    dog_card = page.locator(
        '[data-testid^="dog-card-"]'
    ).filter(has_text=dog_name)

    dog_card.locator('[data-testid^="dog-options-"]').click()
    dog_card.locator('[data-testid^="dog-edit-"]').click()

    page.get_by_test_id("dog-name").fill(updated_name)
    page.get_by_test_id("dog-breed").select_option("Husky")
    page.get_by_test_id("dog-age").select_option("Puppy")
    page.get_by_test_id("dog-experience").select_option("Experienced")
    page.get_by_test_id("dog-save").click()

    page.get_by_test_id("link-dogs").click()
    dog_card = page.locator(
        '[data-testid^="dog-card-"]'
    ).filter(has_text=updated_name)

    expect(dog_card).to_have_count(1)
    expect(dog_card.get_by_text(updated_name, exact=True)).to_be_visible()
    expect(dog_card.get_by_text("Husky · Puppy")).to_be_visible()
