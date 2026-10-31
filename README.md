# Account ownership diagnostic for the provided Playwright fixtures

These are diagnostic test files, not another PawCoach application build. The provided fixture chain uses the same `page`; it does not show a separate API-registration context. `load_dotenv()` only loads environment values. The `credentials` and `login` fixtures are not invoked by the supplied editing test's dependency chain.

The equivalent UI flow passed against the available v1.0.3 source in Chromium: new registration, Labrador creation, Husky/Puppy editing, logout, login to an independent existing account, and verification that the new dog is absent there. This does not prove what happens in the user's local test configuration.

## Install into the test project

Back up your current `conftest.py` and `helpers/dogs.py`. Copy the files in this ZIP into `C:\Users\Zsolt\PycharmProjects\pawcoach-playwright-tests`, preserving the folder names. If your real conftest contains additional fixtures beyond those shared, preserve them when integrating this version. Do not copy these files into the React app.

Keep your existing `.env`, pytest configuration and installed Playwright environment. `PAWCOACH_EMAIL` / `PAWCOACH_PASSWORD` must identify your existing account; the new test accounts get unique generated emails.

From the test project, while PawCoach is running:

```powershell
python -m pytest tests/test_account_isolation_diagnostic.py -v -s --headed --base-url http://127.0.0.1:8000 -x
```

Two tests are included: editing with identity checks, then a real logout/login check that the fresh test dog's ID is absent from your existing account. To run only the second test:

```powershell
python -m pytest tests/test_account_isolation_diagnostic.py::test_new_dog_is_not_in_existing_account -v -s --headed --base-url http://127.0.0.1:8000
```

The diagnostic creates test accounts/dogs and leaves them for inspection. It does not delete or reassign existing data. It logs account IDs/emails, dog IDs and the non-secret expected-account header, not passwords or session cookies. Inspect output before sharing it publicly.

## How to read the first failure

| First failure | What it establishes |
| --- | --- |
| Already authenticated before registration | This test's page started with inherited login state. Inspect custom page/context fixtures, autouse fixtures and storage_state. |
| Registration is not HTTP 201 / email differs | Registration did not create the requested account. Stop before dog creation. |
| After registration account ID/email differs | Browser session is different from the account returned by registration. |
| Before dog creation account differs | Something changed the browser session between fixture stages. |
| Expected-account header missing/wrong | Browser frontend does not send the v1.0.3 account guard for this request. The health endpoint verifies the backend version only. Check the full frontend/dist installation and browser reload. |
| HTTP 409 session_changed during saving | The stale-session guard rejected the write. The dog was not created by that rejected request. |
| After dog creation account changed | Session changed during the save flow. |
| New dog's ID appears in existing account's API dog list | A verified server-side ownership failure under the captured identities; send the printed IDs/statuses and first traceback. |
| API list is correct but UI card remains | A display/cache issue rather than the API returning the dog for the old owner. |

If both diagnostic tests pass but the original suite fails, send `pytest.ini` or `pyproject.toml`, the full test command, and any other autouse/session/context fixtures. Do not assume an account mix-up from a card name alone: compare the registered account ID, current account ID and dog ID.

Compatibility: `user_with_dog` still returns the dog's name. `register_user` still returns the user dictionary, now augmented with `account_id` / `dog_id` for assertions. `create_dog(page, name)` remains supported; the new expected-account argument is optional. The existing fixture names remain available.

Validation: Python source syntax checked; the equivalent UI operations and the v1.0.3 expected-account header were checked in Chromium. No external repository or user database was modified while preparing this pack.
