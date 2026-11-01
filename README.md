# PawCoach Playwright Tests

UI and API regression tests for the PawCoach React/FastAPI application.

## Setup
Install `requirements-test.txt`, install Chromium with `python -m playwright install chromium`, and start the app on `http://127.0.0.1:8000`.

Set `PAWCOACH_EMAIL` and `PAWCOACH_PASSWORD` as environment variables (or in a local `.env` file, never commit it). The existing account must be registered before running the full suite.

Run: `python -m pytest tests/ -v`

## Structure
- `tests/api/`: isolated API tests; `api_user` fixture is defined only in `tests/api/conftest.py`.
- `tests/ui/`: Playwright browser tests.
- `helpers/`: UI test helpers and account checks.
- `.github/workflows/playwright.yml`: GitHub Actions CI.

## Notes
The PATCH dog update payload follows the `DogProfile` schema found in the supplied PawCoach React v1.0.3 backend reference. If the deployed backend differs, inspect its OpenAPI schema. The test is intentionally **not** skipped or marked as passing on HTTP 422.

The training helper has a 100-step safety limit; it is not a fixed expected lesson length. A small PNG fixture is included for the dog-photo upload test.

The test suite requires a running PawCoach backend; static checks alone cannot prove integration tests pass.
