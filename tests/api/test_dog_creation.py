import uuid

from playwright.sync_api import Playwright


def test_create_dog_api(
    playwright: Playwright,
    base_url,
):
    request = playwright.request.new_context(base_url=base_url)

    try:
        # Create a unique test account.
        email = f"dog_api_{uuid.uuid4().hex}@example.com"
        password = f"Test_{uuid.uuid4().hex}!Aa1"

        register_response = request.post(
            "/api/auth/register",
            data={
                "email": email,
                "password": password,
                "confirm_password": password,
                "language": "en",
            },
        )

        assert register_response.status == 201, (
            f"Registration failed: HTTP {register_response.status}"
        )

        # Log in using the new account.
        login_response = request.post(
            "/api/auth/login",
            data={
                "email": email,
                "password": password,
                "language": "en",
            },
        )

        assert login_response.status == 200, (
            f"Login failed: HTTP {login_response.status}"
        )

        # Create a dog through the API.
        dog_name = f"Buddy_{uuid.uuid4().hex[:8]}"

        dog_data = {
            "name": dog_name,
            "breed": "Labrador",
            "age_group": "Adult",
            "training_level": "Brand new",
            "creation_key": uuid.uuid4().hex,
        }

        create_response = request.post(
            "/api/dogs",
            data=dog_data,
        )

        assert create_response.status in (200, 201), (
            f"Dog creation failed: HTTP {create_response.status}. "
            f"Response: {create_response.text()}"
        )

        # Retrieve the authenticated user's dogs.
        list_response = request.get("/api/dogs")

        assert list_response.status == 200, (
            f"Dog retrieval failed: HTTP {list_response.status}"
        )

        response_body = list_response.json()

        dogs = (
            response_body
            if isinstance(response_body, list)
            else response_body["dogs"]
        )

        # Find the newly created dog.
        created_dogs = [
            dog for dog in dogs
            if dog["name"] == dog_name
        ]

        assert len(created_dogs) == 1, (
            f"Expected exactly one dog named {dog_name}, "
            f"found {len(created_dogs)}"
        )

        created_dog = created_dogs[0]

        # Verify the stored attributes.
        assert created_dog["name"] == dog_data["name"]
        assert created_dog["breed"] == dog_data["breed"]
        assert created_dog["age_group"] == dog_data["age_group"]
        assert created_dog["training_level"] == dog_data["training_level"]

        # Verify the dog has an identifier.
        assert "id" in created_dog
        assert created_dog["id"] is not None

    finally:
        request.dispose()
