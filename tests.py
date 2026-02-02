"""
Rithm Test Suite
================
Tests for the music theory education platform.
"""

from django.test import TestCase, Client
from django.urls import reverse, resolve
import os


class URLRoutingTests(TestCase):
    """Test that all URLs resolve correctly."""
    
    def test_landing_page_url_resolves(self):
        """Landing page URL should resolve."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_note_identification_url_resolves(self):
        """Note identification URL should resolve."""
        response = self.client.get('/note_identification/')
        self.assertEqual(response.status_code, 200)
    
    def test_synth_url_resolves(self):
        """Synth URL should resolve."""
        response = self.client.get('/synth/')
        self.assertEqual(response.status_code, 200)
    
    def test_pitch_identification_url_resolves(self):
        """Pitch identification URL should resolve."""
        response = self.client.get('/pitch_identification/')
        self.assertEqual(response.status_code, 200)


class LandingPageTests(TestCase):
    """Tests for the landing page."""
    
    def setUp(self):
        self.client = Client()
        self.response = self.client.get('/')
    
    def test_landing_page_status_code(self):
        """Landing page should return 200."""
        self.assertEqual(self.response.status_code, 200)
    
    def test_landing_page_contains_title(self):
        """Landing page should contain R.I.T.H.M title."""
        self.assertContains(self.response, 'R.I.T.H.M')
    
    def test_landing_page_contains_nav_links(self):
        """Landing page should contain navigation links."""
        self.assertContains(self.response, '/note_identification/')
        self.assertContains(self.response, '/synth/')
        self.assertContains(self.response, '/pitch_identification/')
    
    def test_landing_page_uses_correct_template(self):
        """Landing page should use the correct template."""
        self.assertTemplateUsed(self.response, 'landing_page/index.html')
        self.assertTemplateUsed(self.response, 'base.html')


class NoteIdentificationTests(TestCase):
    """Tests for the note identification game."""
    
    def setUp(self):
        self.client = Client()
        self.response = self.client.get('/note_identification/')
    
    def test_note_identification_status_code(self):
        """Note identification page should return 200."""
        self.assertEqual(self.response.status_code, 200)
    
    def test_note_identification_uses_correct_template(self):
        """Note identification should use correct template."""
        self.assertTemplateUsed(self.response, 'note_identification/index.html')
    
    def test_note_identification_contains_difficulty_buttons(self):
        """Page should contain difficulty selection buttons."""
        self.assertContains(self.response, 'Beginner')
        self.assertContains(self.response, 'Intermediate')
        self.assertContains(self.response, 'Advanced')
    
    def test_note_identification_contains_note_buttons(self):
        """Page should contain note answer buttons."""
        # Natural notes
        for note in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
            self.assertContains(self.response, f'data-note="{note}"')
    
    def test_note_identification_contains_stats(self):
        """Page should contain stats display elements."""
        self.assertContains(self.response, 'id="score"')
        self.assertContains(self.response, 'id="streak"')
        self.assertContains(self.response, 'id="accuracy"')
    
    def test_note_identification_contains_javascript(self):
        """Page should contain game JavaScript."""
        self.assertContains(self.response, 'setDifficulty')
        self.assertContains(self.response, 'checkAnswer')
        self.assertContains(self.response, 'nextNote')


class SynthesizerTests(TestCase):
    """Tests for the web synthesizer."""
    
    def setUp(self):
        self.client = Client()
        self.response = self.client.get('/synth/')
    
    def test_synth_status_code(self):
        """Synth page should return 200."""
        self.assertEqual(self.response.status_code, 200)
    
    def test_synth_uses_correct_template(self):
        """Synth should use correct template."""
        self.assertTemplateUsed(self.response, 'synth/index.html')
    
    def test_synth_contains_keyboard(self):
        """Synth page should contain keyboard elements."""
        self.assertContains(self.response, 'key_container')
    
    def test_synth_contains_tone_js(self):
        """Synth page should include Tone.js library."""
        self.assertContains(self.response, 'Tone.js')
    
    def test_synth_contains_synth_types(self):
        """Synth page should have multiple synth types."""
        self.assertContains(self.response, 'poly_synth')
        self.assertContains(self.response, 'FM_synth')


class PitchIdentificationTests(TestCase):
    """Tests for the pitch identification module."""
    
    def setUp(self):
        self.client = Client()
        self.response = self.client.get('/pitch_identification/')
    
    def test_pitch_identification_status_code(self):
        """Pitch identification page should return 200."""
        self.assertEqual(self.response.status_code, 200)
    
    def test_pitch_identification_uses_correct_template(self):
        """Pitch identification should use correct template."""
        self.assertTemplateUsed(self.response, 'pitch_identification/index.html')


class StaticFilesTests(TestCase):
    """Tests for static file availability."""
    
    def test_note_images_exist(self):
        """Verify note images exist in staticfiles."""
        static_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'staticfiles', 'note_identification'
        )
        
        if os.path.exists(static_path):
            expected_notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
            for note in expected_notes:
                note_file = os.path.join(static_path, f'{note}.png')
                self.assertTrue(
                    os.path.exists(note_file),
                    f"Note image {note}.png should exist"
                )


class BaseTemplateTests(TestCase):
    """Tests for the base template."""
    
    def setUp(self):
        self.client = Client()
        self.response = self.client.get('/')
    
    def test_base_template_contains_bootstrap(self):
        """Base template should include Bootstrap CSS."""
        self.assertContains(self.response, 'bootstrap')
    
    def test_base_template_contains_navbar(self):
        """Base template should contain navigation bar."""
        self.assertContains(self.response, 'navbar')
    
    def test_base_template_contains_brand(self):
        """Base template should contain brand link."""
        self.assertContains(self.response, 'navbar-brand')


class NavigationTests(TestCase):
    """Tests for site navigation."""
    
    def test_can_navigate_from_landing_to_note_identification(self):
        """Should be able to navigate from landing to note identification."""
        response = self.client.get('/')
        self.assertContains(response, 'href="/note_identification/"')
    
    def test_can_navigate_from_landing_to_synth(self):
        """Should be able to navigate from landing to synth."""
        response = self.client.get('/')
        self.assertContains(response, 'href="/synth/"')
    
    def test_can_navigate_from_landing_to_pitch_identification(self):
        """Should be able to navigate from landing to pitch identification."""
        response = self.client.get('/')
        self.assertContains(response, 'href="/pitch_identification/"')
    
    def test_navbar_present_on_all_pages(self):
        """Navbar should be present on all pages."""
        pages = ['/', '/note_identification/', '/synth/', '/pitch_identification/']
        for page in pages:
            response = self.client.get(page)
            self.assertContains(response, 'navbar', msg_prefix=f"Page {page}")


class AuthenticationTests(TestCase):
    """Tests for user authentication."""
    
    def test_login_page_loads(self):
        """Login page should load correctly."""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign In')
    
    def test_register_page_loads(self):
        """Register page should load correctly."""
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')
    
    def test_user_can_register(self):
        """User should be able to register."""
        response = self.client.post('/accounts/register/', {
            'username': 'testuser',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        from django.contrib.auth.models import User
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_user_can_login(self):
        """User should be able to login."""
        from django.contrib.auth.models import User
        User.objects.create_user('testuser', password='testpass123!')
        
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
    
    def test_profile_requires_login(self):
        """Profile page should require authentication."""
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_accessible_when_logged_in(self):
        """Profile should be accessible when logged in."""
        from django.contrib.auth.models import User
        user = User.objects.create_user('testuser', password='testpass123!')
        self.client.login(username='testuser', password='testpass123!')
        
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    # Edge case tests
    def test_register_password_mismatch(self):
        """Registration should fail if passwords don't match."""
        response = self.client.post('/accounts/register/', {
            'username': 'testuser',
            'password1': 'testpass123!',
            'password2': 'differentpass!'
        })
        self.assertEqual(response.status_code, 200)  # Stays on page
        
        from django.contrib.auth.models import User
        self.assertFalse(User.objects.filter(username='testuser').exists())
    
    def test_register_weak_password(self):
        """Registration should fail with weak password."""
        response = self.client.post('/accounts/register/', {
            'username': 'testuser',
            'password1': '123',
            'password2': '123'
        })
        self.assertEqual(response.status_code, 200)  # Stays on page
        
        from django.contrib.auth.models import User
        self.assertFalse(User.objects.filter(username='testuser').exists())
    
    def test_register_duplicate_username(self):
        """Registration should fail if username already exists."""
        from django.contrib.auth.models import User
        User.objects.create_user('testuser', password='testpass123!')
        
        response = self.client.post('/accounts/register/', {
            'username': 'testuser',
            'password1': 'anotherpass123!',
            'password2': 'anotherpass123!'
        })
        self.assertEqual(response.status_code, 200)  # Stays on page
        self.assertEqual(User.objects.filter(username='testuser').count(), 1)
    
    def test_login_wrong_password(self):
        """Login should fail with wrong password."""
        from django.contrib.auth.models import User
        User.objects.create_user('testuser', password='testpass123!')
        
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stays on page
    
    def test_login_nonexistent_user(self):
        """Login should fail for nonexistent user."""
        response = self.client.post('/accounts/login/', {
            'username': 'doesnotexist',
            'password': 'anypassword'
        })
        self.assertEqual(response.status_code, 200)  # Stays on page
    
    def test_logout_clears_session(self):
        """Logout should clear the session."""
        from django.contrib.auth.models import User
        User.objects.create_user('testuser', password='testpass123!')
        self.client.login(username='testuser', password='testpass123!')
        
        # Verify logged in
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        
        # Logout
        self.client.get('/accounts/logout/')
        
        # Profile should now redirect
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 302)
    
    def test_authenticated_user_redirected_from_login(self):
        """Already authenticated user should be redirected from login page."""
        from django.contrib.auth.models import User
        User.objects.create_user('testuser', password='testpass123!')
        self.client.login(username='testuser', password='testpass123!')
        
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 302)
    
    def test_authenticated_user_redirected_from_register(self):
        """Already authenticated user should be redirected from register page."""
        from django.contrib.auth.models import User
        User.objects.create_user('testuser', password='testpass123!')
        self.client.login(username='testuser', password='testpass123!')
        
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 302)
    
    def test_login_redirect_next(self):
        """Login should redirect to 'next' parameter if provided."""
        from django.contrib.auth.models import User
        User.objects.create_user('testuser', password='testpass123!')
        
        response = self.client.post('/accounts/login/?next=/note_identification/', {
            'username': 'testuser',
            'password': 'testpass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/note_identification/')


class UserProfileTests(TestCase):
    """Tests for user profile and game stats."""
    
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user('testuser', password='testpass123!')
        self.client.login(username='testuser', password='testpass123!')
    
    def test_profile_created_on_user_creation(self):
        """Profile should be auto-created when user is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
    
    def test_profile_default_values(self):
        """Profile should have correct default values."""
        profile = self.user.profile
        self.assertEqual(profile.note_total_correct, 0)
        self.assertEqual(profile.note_best_streak, 0)
        self.assertEqual(profile.note_difficulty, 'beginner')
    
    def test_get_stats_api(self):
        """Should be able to get stats via API."""
        response = self.client.get('/accounts/api/note-stats/')
        self.assertEqual(response.status_code, 200)
        
        import json
        data = json.loads(response.content)
        self.assertTrue(data['authenticated'])
        self.assertIn('stats', data)
    
    def test_update_stats_api(self):
        """Should be able to update stats via API."""
        import json
        response = self.client.post(
            '/accounts/api/note-stats/update/',
            data=json.dumps({
                'correct': 10,
                'total': 15,
                'bestStreak': 5
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify stats were updated
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.note_total_correct, 10)
        self.assertEqual(self.user.profile.note_best_streak, 5)
    
    def test_stats_api_unauthenticated(self):
        """Stats API should reject unauthenticated requests for updates."""
        import json
        self.client.logout()
        
        response = self.client.post(
            '/accounts/api/note-stats/update/',
            data=json.dumps({'correct': 100}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
    
    def test_get_stats_api_unauthenticated(self):
        """Get stats API should indicate not authenticated."""
        import json
        self.client.logout()
        
        response = self.client.get('/accounts/api/note-stats/')
        data = json.loads(response.content)
        self.assertFalse(data['authenticated'])
    
    def test_best_streak_only_increases(self):
        """Best streak should only increase, never decrease."""
        import json
        
        # Set initial best streak to 10
        self.client.post(
            '/accounts/api/note-stats/update/',
            data=json.dumps({'bestStreak': 10}),
            content_type='application/json'
        )
        
        # Try to set it lower
        self.client.post(
            '/accounts/api/note-stats/update/',
            data=json.dumps({'bestStreak': 5}),
            content_type='application/json'
        )
        
        # Should still be 10
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.note_best_streak, 10)
    
    def test_difficulty_saved(self):
        """Difficulty preference should be saved."""
        import json
        
        self.client.post(
            '/accounts/api/note-stats/update/',
            data=json.dumps({'difficulty': 'advanced'}),
            content_type='application/json'
        )
        
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.note_difficulty, 'advanced')
    
    def test_accuracy_calculation(self):
        """Accuracy should be calculated correctly."""
        profile = self.user.profile
        profile.note_total_correct = 7
        profile.note_total_attempts = 10
        profile.save()
        
        self.assertEqual(profile.note_accuracy, 70)
    
    def test_accuracy_zero_attempts(self):
        """Accuracy should be 0 with no attempts."""
        profile = self.user.profile
        self.assertEqual(profile.note_accuracy, 0)
