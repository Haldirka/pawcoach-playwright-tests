

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
