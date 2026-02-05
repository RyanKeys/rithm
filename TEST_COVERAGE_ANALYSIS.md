# Test Coverage Analysis

## Current State

**Test runner:** Django TestCase (unittest-based), run via `python manage.py test`
**Total tests:** 55 (54 passing, 1 failing)
**Test location:** All real tests live in the root `tests.py`. The 8 app-level `tests.py` files are empty placeholders.

### Existing Test Classes

| Test Class | Tests | What It Covers |
|---|---|---|
| `URLRoutingTests` | 4 | Basic 200 checks for `/`, `/note_identification/`, `/synth/`, `/pitch_identification/` |
| `LandingPageTests` | 4 | Status code, title text, nav links, template used |
| `NoteIdentificationTests` | 6 | Status, template, difficulty buttons, note buttons, stats elements, JS functions |
| `SynthesizerTests` | 5 | Status, template, keyboard elements, Tone.js inclusion, synth types |
| `PitchIdentificationTests` | 2 | Status code, template |
| `StaticFilesTests` | 1 | Note image files exist on disk |
| `BaseTemplateTests` | 3 | Bootstrap CSS, navbar, brand link |
| `NavigationTests` | 4 | Cross-page navigation links, navbar on all pages |
| `AuthenticationTests` | 16 | Login/register/logout flows, redirects, password validation, duplicate checks |
| `UserProfileTests` | 10 | Profile auto-creation, defaults, note stats API (get/update), streaks, accuracy |

### Failing Test

`test_user_can_register` expects a `302` redirect after registration, but the app now uses email verification which renders a `verification_sent.html` page (status `200`). This test needs to be updated to match the current registration flow.

---

## Coverage Gaps (Ranked by Priority)

### 1. Leaderboard App — NO TESTS (HIGH PRIORITY)

The entire `leaderboard/` app has zero test coverage. This is the most significant gap because it contains complex business logic, database aggregation queries, and multiple API endpoints.

**What needs tests:**

- **`Score` model** (`leaderboard/models.py:6`): Auto-calculated `accuracy` field in `save()`, model ordering, `__str__` representation
- **`WeeklyScore` model** (`leaderboard/models.py:54`): `unique_together` constraint, accuracy calculation on save, week aggregation logic
- **`leaderboard_view`** (`leaderboard/views.py:18`): Filtering by game/difficulty/period, weekly vs all-time ranking, invalid parameter handling, authenticated user rank detection
- **`submit_score` API** (`leaderboard/views.py:98`): Authentication requirement, input validation (invalid game, invalid difficulty, minimum 10 attempts), Score creation, WeeklyScore update/creation, rank calculation
- **`api_leaderboard` API** (`leaderboard/views.py:169`): Weekly/all-time filtering, limit parameter, JSON response format
- **`get_week_start` utility** (`leaderboard/views.py:11`): Edge cases around Monday boundaries

**Example tests to add:**
```python
class ScoreModelTests(TestCase):
    def test_accuracy_calculated_on_save(self):
        """Score.accuracy should be auto-calculated from correct/total."""

    def test_accuracy_zero_when_no_attempts(self):
        """Score.accuracy should default to 0 when total is 0."""

class SubmitScoreAPITests(TestCase):
    def test_submit_score_unauthenticated(self):
        """Should return 401 for unauthenticated users."""

    def test_submit_score_invalid_game(self):
        """Should return 400 for invalid game type."""

    def test_submit_score_below_minimum_attempts(self):
        """Should reject scores with fewer than 10 attempts."""

    def test_submit_score_creates_weekly_score(self):
        """Should create/update WeeklyScore entry."""

    def test_submit_score_returns_rank(self):
        """Should return the user's rank after submission."""

class LeaderboardViewTests(TestCase):
    def test_leaderboard_page_loads(self):
        """Leaderboard page should return 200."""

    def test_leaderboard_filters_by_game(self):
        """Should filter scores by game parameter."""

    def test_leaderboard_weekly_vs_alltime(self):
        """Weekly and all-time should return different result sets."""

    def test_invalid_difficulty_defaults_to_beginner(self):
        """Invalid difficulty param should fall back to beginner."""
```

### 2. Email Verification System — NO TESTS (HIGH PRIORITY)

The email verification flow (`accounts/models.py:9-30`, `accounts/views.py:18-51`, `accounts/views.py:94-136`) is entirely untested. This is a security-critical feature.

**What needs tests:**

- **`EmailVerification.is_expired()`** (`accounts/models.py:16`): Token expiry after 24 hours
- **`EmailVerification.verify()`** (`accounts/models.py:21`): Sets `verified_at`, activates user
- **`verify_email` view** (`accounts/views.py:94`): Valid token verification, already-verified token, expired token, invalid token
- **`resend_verification` view** (`accounts/views.py:119`): Resending for inactive user, non-existent email (should not reveal info), GET vs POST
- **`send_verification_email` function** (`accounts/views.py:18`): Email sending success/failure, token regeneration on resend

**Example tests to add:**
```python
class EmailVerificationModelTests(TestCase):
    def test_token_not_expired_within_24_hours(self):
        """Token should be valid within 24 hours."""

    def test_token_expired_after_24_hours(self):
        """Token should be expired after 24 hours."""

    def test_verify_activates_user(self):
        """Calling verify() should set is_active=True."""

class VerifyEmailViewTests(TestCase):
    def test_valid_token_verifies_user(self):
        """Valid token should verify user and redirect to login."""

    def test_expired_token_deletes_user(self):
        """Expired token should delete user and redirect to register."""

    def test_already_verified_redirects_to_login(self):
        """Already verified token should redirect to login with info message."""

    def test_invalid_token_returns_404(self):
        """Invalid/nonexistent token should return 404."""

class ResendVerificationTests(TestCase):
    def test_resend_for_inactive_user(self):
        """Should resend verification for inactive user."""

    def test_resend_unknown_email_no_info_leak(self):
        """Should not reveal whether email exists in system."""
```

### 3. Interval Stats API — NO TESTS (MEDIUM PRIORITY)

The interval training stats endpoints (`accounts/views.py:238-294`) mirror the note stats API but have zero test coverage. The note stats API is tested but the interval counterpart is not.

**What needs tests:**

- **`update_interval_stats`** (`accounts/views.py:238`): Authentication, stat updates, best streak logic, difficulty saving
- **`get_interval_stats`** (`accounts/views.py:278`): Authenticated vs unauthenticated responses
- **`UserProfile.interval_accuracy`** property (`accounts/models.py:76`): Accuracy calculation for intervals

### 4. Landing Page Content Pages — NO TESTS (MEDIUM PRIORITY)

Three content pages have no test coverage:

- **`music_theory_guide`** (`landing_page/views.py:26`) — `/guide/`
- **`practice_tips`** (`landing_page/views.py:32`) — `/tips/`
- **`faq`** (`landing_page/views.py:36`) — `/faq/`
- **`ShowTimeView`** (`landing_page/views.py:18`) — Not routed but exists in code

**What needs tests:**
```python
class ContentPageTests(TestCase):
    def test_guide_page_loads(self):
        response = self.client.get('/guide/')
        self.assertEqual(response.status_code, 200)

    def test_tips_page_loads(self):
        response = self.client.get('/tips/')
        self.assertEqual(response.status_code, 200)

    def test_faq_page_loads(self):
        response = self.client.get('/faq/')
        self.assertEqual(response.status_code, 200)
```

### 5. Chord Identification & Interval Training Pages — NO TESTS (MEDIUM PRIORITY)

These two game pages have no URL routing or template tests at all (unlike note identification, pitch identification, and synth which do).

**What needs tests:**

- `/chord_identification/` — status code, template, page content
- `/interval_training/` — status code, template, page content

### 6. Registration Form Validation — INDIRECT ONLY (LOW PRIORITY)

`RegistrationForm.clean_email()` (`accounts/forms.py:20`) is tested indirectly through the view's duplicate-email test, but there are no isolated form-level tests.

**What needs tests:**
```python
class RegistrationFormTests(TestCase):
    def test_form_valid_with_all_fields(self):
        """Form should be valid with proper inputs."""

    def test_form_invalid_without_email(self):
        """Form should require email."""

    def test_form_rejects_duplicate_email(self):
        """clean_email should raise ValidationError for existing email."""

    def test_form_saves_email_to_user(self):
        """save() should set email on the User object."""
```

### 7. API Edge Cases & Error Handling — NOT TESTED (LOW PRIORITY)

No tests cover malformed input or HTTP method enforcement:

- **Malformed JSON** to `/accounts/api/note-stats/update/` or `/leaderboard/api/submit/`
- **GET requests** to POST-only endpoints (should return 405)
- **Empty body** on POST endpoints
- **Pitch stats API** (`accounts/views.py` — if pitch stats endpoints exist similar to note/interval, they need tests too; currently no pitch stats API endpoints are defined)

### 8. Error Page Templates — NOT TESTED (LOW PRIORITY)

Custom error templates exist (`templates/400.html`, `403.html`, `404.html`, `500.html`) but none are tested.

### 9. `Game` Model — NOT TESTED (LOW PRIORITY)

The `Game` model (`landing_page/models.py:7`) is used by the landing page `IndexView` but has no model-level tests.

---

## Structural Recommendations

1. **Move tests into app directories.** The monolithic root `tests.py` should be split so each app owns its tests. This improves discoverability and makes it easier to run targeted test suites (`python manage.py test leaderboard`).

2. **Fix the failing test.** `test_user_can_register` (`tests.py:229`) needs updating to account for the email verification flow — it should expect a `200` with the `verification_sent.html` template instead of a `302` redirect.

3. **Add `coverage.py` to the project.** Install `coverage` and add a configuration to `setup.cfg` or `pyproject.toml` so you can run `coverage run manage.py test && coverage report` to get quantitative coverage metrics going forward.

---

## Summary

| Area | Current Coverage | Priority |
|---|---|---|
| Leaderboard (models, views, APIs) | None | **High** |
| Email verification (model, views) | None | **High** |
| Interval stats API | None | **Medium** |
| Content pages (guide, tips, FAQ) | None | **Medium** |
| Chord identification page | None | **Medium** |
| Interval training page | None | **Medium** |
| Registration form (isolated) | Indirect only | Low |
| API error handling / edge cases | None | Low |
| Error page templates | None | Low |
| Game model | None | Low |
