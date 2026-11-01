
import uuid

from playwright.sync_api import Playwright


def extract_dogs(response_body):
    if isinstance(response_body, list):
        return response_body

    return response_body["dogs"]


def test_cross_account_dog_access(
    playwright: Playwright,
    base_url,
):
    user_a = playwright.request.new_context(base_url=base_url)
    user_b = playwright.request.new_context(base_url=base_url)

    try:
        account_ids = []

        # Register and log in two independent users.
        for context in (user_a, user_b):
            email = f"api_test_{uuid.uuid4().hex}@example.com"
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
                f"Registration failed: HTTP "
                f"{register_response.status}"
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
                f"Login failed: HTTP {login_response.status}"
            )

            login_data = login_response.json()

            assert "id" in login_data, (
                "Login response does not contain an account ID"
            )

            account_ids.append(login_data["id"])

        user_a_account_id = account_ids[0]
        user_b_account_id = account_ids[1]

        assert user_a_account_id != user_b_account_id, (
            "Both users have the same account ID"
        )

        # User A creates a dog.
        dog_name = f"Buddy_{uuid.uuid4().hex[:8]}"

        create_response = user_a.post(
            "/api/dogs",
            data={
                "name": dog_name,
                "breed": "Labrador",
                "age_group": "Adult",
                "training_level": "Brand new",
                "creation_key": uuid.uuid4().hex,
            },
        )

        assert create_response.status in (200, 201), (
            f"Dog creation failed: HTTP "
            f"{create_response.status}"
        )

        # Verify User A can see the newly created dog.
        user_a_response = user_a.get("/api/dogs")

        assert user_a_response.status == 200

        user_a_dogs = extract_dogs(user_a_response.json())

        assert any(
            dog["name"] == dog_name
            for dog in user_a_dogs
        ), "User A cannot see their newly created dog"

        # Verify User B cannot see User A's dog normally.
        user_b_response = user_b.get("/api/dogs")

        assert user_b_response.status == 200

        user_b_dogs = extract_dogs(user_b_response.json())

        assert not any(
            dog["name"] == dog_name
            for dog in user_b_dogs
        ), (
            "SECURITY BUG: User B can see User A's dog"
        )

        # User B attempts to impersonate User A by supplying
        # User A's account ID in the request header.
        spoofed_response = user_b.get(
            "/api/dogs",
            headers={
                "X-PawCoach-Account": str(user_a_account_id),
            },
        )

        # User B attempts to access User A's account.
        spoofed_response = user_b.get(
            "/api/dogs",
            headers={
                "X-PawCoach-Account": str(user_a_account_id),
            },
        )

        assert spoofed_response.status == 409, (
            f"Expected 409 Conflict, got {spoofed_response.status}"
        )

        assert spoofed_response.json()["detail"]["code"] == "session_changed"

        # A 200 response is acceptable only if the API
        # still returns data belonging to User B.
        if spoofed_response.status == 200:
            spoofed_dogs = extract_dogs(
                spoofed_response.json()
            )

            assert not any(
                dog["name"] == dog_name
                for dog in spoofed_dogs
            ), (
                "SECURITY BUG: User B accessed User A's "
                "dog using a spoofed X-PawCoach-Account header"
            )

    finally:
        user_a.dispose()
        user_b.dispose()
