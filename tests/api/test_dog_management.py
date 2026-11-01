
import uuid

from playwright.sync_api import expect


def dog_payload():
    return {
        "name": f"Buddy_{uuid.uuid4().hex[:8]}",
        "breed": "Labrador",
        "age_group": "Adult",
        "training_level": "Brand new",
        "creation_key": uuid.uuid4().hex,
    }


def get_dogs(api_user):
    response = api_user.get("/api/dogs")
    assert response.status == 200

    body = response.json()
    return body if isinstance(body, list) else body["dogs"]


def create_dog(api_user):
    payload = dog_payload()
    response = api_user.post("/api/dogs", data=payload)

    assert response.status in (200, 201), (
        f"Dog creation failed: {response.status}"
    )

    dogs = get_dogs(api_user)
    dog = next(
        (dog for dog in dogs if dog["name"] == payload["name"]),
        None,
    )

    assert dog is not None, "Created dog was not found"
    assert "id" in dog

    return dog, payload


def test_update_dog(api_user):
    dog, original = create_dog(api_user)

    updated_name = f"Updated_{uuid.uuid4().hex[:8]}"

    update_data = {
        "name": updated_name,
        "breed": original["breed"],
        "age_group": original["age_group"],
        "training_level": original["training_level"],
    }

    response = api_user.patch(
        f"/api/dogs/{dog['id']}",
        data=update_data,
    )

    assert response.status in (200, 204), (
        f"Dog update failed: {response.status}. "
        f"Response: {response.text()}"
    )

    updated = next(
        item
        for item in get_dogs(api_user)
        if item["id"] == dog["id"]
    )

    assert updated["name"] == updated_name
    assert updated["breed"] == original["breed"]
    assert updated["age_group"] == original["age_group"]
    assert updated["training_level"] == original["training_level"]


def test_delete_dog(api_user):
    dog, _ = create_dog(api_user)

    # Verify the actual delete route in Swagger.
    response = api_user.delete(
        f"/api/dogs/{dog['id']}"
    )

    assert response.status in (200, 204), (
        f"Dog deletion failed: {response.status}"
    )

    dog_ids = [
        item["id"] for item in get_dogs(api_user)
    ]

    assert dog["id"] not in dog_ids


def test_unauthenticated_dog_access(playwright, base_url):
    anonymous = playwright.request.new_context(base_url=base_url)

    try:
        response = anonymous.get("/api/dogs")

        assert response.status in (401, 403), (
            "SECURITY BUG: Unauthenticated request "
            f"returned HTTP {response.status}"
        )

    finally:
        anonymous.dispose()


def test_invalid_dog_creation(api_user):
    before = get_dogs(api_user)

    response = api_user.post(
        "/api/dogs",
        data={
            "name": "",
            "breed": "Labrador",
            "age_group": "Adult",
            "training_level": "Brand new",
            "creation_key": uuid.uuid4().hex,
        },
    )

    assert response.status in (400, 422), (
        f"Invalid dog creation returned {response.status}"
    )

    after = get_dogs(api_user)

    assert len(after) == len(before), (
        "Invalid request unexpectedly created a dog"
    )


def test_duplicate_dog_creation(api_user):
    payload = dog_payload()

    first = api_user.post("/api/dogs", data=payload)
    second = api_user.post("/api/dogs", data=payload)

    assert first.status in (200, 201)

    # Depending on the creation_key contract, the second
    # request may return the existing dog or a conflict.
    assert second.status in (200, 201, 409), (
        f"Unexpected duplicate response: {second.status}"
    )

    matching_dogs = [
        dog
        for dog in get_dogs(api_user)
        if dog["name"] == payload["name"]
    ]

    assert len(matching_dogs) == 1, (
        "Duplicate request created multiple dogs"
    )
