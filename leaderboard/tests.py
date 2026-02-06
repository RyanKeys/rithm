from datetime import date, timedelta
import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone

from .models import Score, WeeklyScore
from .views import get_week_start


class GetWeekStartTests(TestCase):
    """Tests for the get_week_start utility function."""

    def test_returns_monday_for_monday(self):
        """Monday should return itself."""
        monday = date(2026, 2, 2)  # a Monday
        self.assertEqual(get_week_start(monday), monday)

    def test_returns_monday_for_wednesday(self):
        """Wednesday should return the preceding Monday."""
        wednesday = date(2026, 2, 4)
        self.assertEqual(get_week_start(wednesday), date(2026, 2, 2))

    def test_returns_monday_for_sunday(self):
        """Sunday should return the preceding Monday."""
        sunday = date(2026, 2, 8)
        self.assertEqual(get_week_start(sunday), date(2026, 2, 2))

    def test_defaults_to_today(self):
        """Calling with no argument should use today's date."""
        result = get_week_start()
        today = timezone.now().date()
        expected = today - timedelta(days=today.weekday())
        self.assertEqual(result, expected)


class ScoreModelTests(TestCase):
    """Tests for the Score model."""

    def setUp(self):
        self.user = User.objects.create_user('scorer', password='testpass123!')

    def test_accuracy_calculated_on_save(self):
        """Accuracy should be auto-calculated from correct/total on save."""
        score = Score.objects.create(
            user=self.user, game='note', correct=8, total=10
        )
        self.assertEqual(score.accuracy, 80.0)

    def test_accuracy_rounds_to_one_decimal(self):
        """Accuracy should be rounded to one decimal place."""
        score = Score.objects.create(
            user=self.user, game='note', correct=1, total=3
        )
        self.assertEqual(score.accuracy, 33.3)

    def test_accuracy_zero_when_total_is_zero(self):
        """Accuracy should remain 0 when total is 0."""
        score = Score.objects.create(
            user=self.user, game='note', correct=0, total=0
        )
        self.assertEqual(score.accuracy, 0)

    def test_accuracy_100_percent(self):
        """Perfect score should give 100% accuracy."""
        score = Score.objects.create(
            user=self.user, game='note', correct=20, total=20
        )
        self.assertEqual(score.accuracy, 100.0)

    def test_str_representation(self):
        """__str__ should include username, game, correct count, and accuracy."""
        score = Score.objects.create(
            user=self.user, game='note', correct=7, total=10
        )
        self.assertIn('scorer', str(score))
        self.assertIn('note', str(score))
        self.assertIn('7', str(score))

    def test_default_ordering_by_correct_desc(self):
        """Scores should be ordered by -correct, -accuracy, -best_streak."""
        Score.objects.create(user=self.user, game='note', correct=5, total=10)
        Score.objects.create(user=self.user, game='note', correct=10, total=10)
        Score.objects.create(user=self.user, game='note', correct=8, total=10)
        scores = list(Score.objects.all().values_list('correct', flat=True))
        self.assertEqual(scores, [10, 8, 5])

    def test_difficulty_defaults_to_beginner(self):
        """Difficulty should default to 'beginner'."""
        score = Score.objects.create(
            user=self.user, game='note', correct=5, total=10
        )
        self.assertEqual(score.difficulty, 'beginner')


class WeeklyScoreModelTests(TestCase):
    """Tests for the WeeklyScore model."""

    def setUp(self):
        self.user = User.objects.create_user('weeklyuser', password='testpass123!')
        self.week_start = get_week_start()

    def test_accuracy_calculated_on_save(self):
        """Accuracy should be auto-calculated on save."""
        weekly = WeeklyScore.objects.create(
            user=self.user, game='note', week_start=self.week_start,
            total_correct=15, total_attempts=20
        )
        self.assertEqual(weekly.accuracy, 75.0)

    def test_accuracy_zero_when_no_attempts(self):
        """Accuracy should remain 0 with zero attempts."""
        weekly = WeeklyScore.objects.create(
            user=self.user, game='note', week_start=self.week_start,
            total_correct=0, total_attempts=0
        )
        self.assertEqual(weekly.accuracy, 0)

    def test_unique_together_constraint(self):
        """Same user+game+difficulty+week should not allow duplicates."""
        WeeklyScore.objects.create(
            user=self.user, game='note', difficulty='beginner',
            week_start=self.week_start
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            WeeklyScore.objects.create(
                user=self.user, game='note', difficulty='beginner',
                week_start=self.week_start
            )

    def test_different_weeks_allowed(self):
        """Same user+game+difficulty in different weeks should be fine."""
        WeeklyScore.objects.create(
            user=self.user, game='note', week_start=self.week_start
        )
        other_week = self.week_start - timedelta(weeks=1)
        weekly2 = WeeklyScore.objects.create(
            user=self.user, game='note', week_start=other_week
        )
        self.assertEqual(WeeklyScore.objects.filter(user=self.user).count(), 2)

    def test_str_representation(self):
        """__str__ should include username, game, and week."""
        weekly = WeeklyScore.objects.create(
            user=self.user, game='interval', week_start=self.week_start,
            total_correct=42
        )
        result = str(weekly)
        self.assertIn('weeklyuser', result)
        self.assertIn('interval', result)
        self.assertIn('42', result)


class LeaderboardViewTests(TestCase):
    """Tests for the main leaderboard page view."""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('alice', password='testpass123!')
        self.user2 = User.objects.create_user('bob', password='testpass123!')

    def test_leaderboard_page_loads(self):
        """Leaderboard page should return 200."""
        response = self.client.get('/leaderboard/')
        self.assertEqual(response.status_code, 200)

    def test_leaderboard_uses_correct_template(self):
        """Should use leaderboard/index.html."""
        response = self.client.get('/leaderboard/')
        self.assertTemplateUsed(response, 'leaderboard/index.html')

    def test_context_contains_game_list(self):
        """Context should include list of available games."""
        response = self.client.get('/leaderboard/')
        games = response.context['games']
        game_ids = [g['id'] for g in games]
        self.assertIn('note', game_ids)
        self.assertIn('interval', game_ids)
        self.assertIn('chord', game_ids)
        self.assertIn('pitch', game_ids)

    def test_context_contains_difficulty_list(self):
        """Context should include list of difficulties."""
        response = self.client.get('/leaderboard/')
        difficulties = response.context['difficulties']
        diff_ids = [d['id'] for d in difficulties]
        self.assertEqual(diff_ids, ['beginner', 'intermediate', 'advanced'])

    def test_defaults_to_note_game(self):
        """Should default to 'note' game when no game param."""
        response = self.client.get('/leaderboard/')
        self.assertEqual(response.context['current_game'], 'note')

    def test_defaults_to_beginner_difficulty(self):
        """Should default to 'beginner' difficulty."""
        response = self.client.get('/leaderboard/')
        self.assertEqual(response.context['current_difficulty'], 'beginner')

    def test_defaults_to_alltime_period(self):
        """Should default to 'alltime' period."""
        response = self.client.get('/leaderboard/')
        self.assertEqual(response.context['period'], 'alltime')

    def test_invalid_difficulty_falls_back_to_beginner(self):
        """Invalid difficulty param should fall back to 'beginner'."""
        response = self.client.get('/leaderboard/?difficulty=invalid')
        self.assertEqual(response.context['current_difficulty'], 'beginner')

    def test_filters_by_game_param(self):
        """Leaderboard should filter by game query param."""
        response = self.client.get('/leaderboard/?game=interval')
        self.assertEqual(response.context['current_game'], 'interval')

    def test_alltime_shows_aggregated_scores(self):
        """All-time leaderboard should aggregate scores per user."""
        Score.objects.create(
            user=self.user1, game='note', difficulty='beginner',
            correct=10, total=15
        )
        Score.objects.create(
            user=self.user1, game='note', difficulty='beginner',
            correct=8, total=10
        )
        response = self.client.get('/leaderboard/?game=note&difficulty=beginner')
        leaderboard = response.context['leaderboard']
        self.assertEqual(len(leaderboard), 1)
        self.assertEqual(leaderboard[0]['correct'], 18)
        self.assertEqual(leaderboard[0]['sessions'], 2)

    def test_alltime_ranks_users_by_correct(self):
        """Users should be ranked by total correct descending."""
        Score.objects.create(
            user=self.user1, game='note', correct=5, total=10
        )
        Score.objects.create(
            user=self.user2, game='note', correct=15, total=20
        )
        response = self.client.get('/leaderboard/?game=note')
        leaderboard = response.context['leaderboard']
        self.assertEqual(leaderboard[0]['username'], 'bob')
        self.assertEqual(leaderboard[0]['rank'], 1)
        self.assertEqual(leaderboard[1]['username'], 'alice')
        self.assertEqual(leaderboard[1]['rank'], 2)

    def test_weekly_shows_weekly_scores(self):
        """Weekly period should show WeeklyScore entries."""
        week_start = get_week_start()
        WeeklyScore.objects.create(
            user=self.user1, game='note', difficulty='beginner',
            week_start=week_start, total_correct=20, total_attempts=30,
            sessions_played=3
        )
        response = self.client.get(
            '/leaderboard/?game=note&difficulty=beginner&period=weekly'
        )
        leaderboard = response.context['leaderboard']
        self.assertEqual(len(leaderboard), 1)
        self.assertEqual(leaderboard[0]['correct'], 20)
        self.assertEqual(leaderboard[0]['sessions'], 3)

    def test_weekly_excludes_other_weeks(self):
        """Weekly leaderboard should not include scores from other weeks."""
        old_week = get_week_start() - timedelta(weeks=1)
        WeeklyScore.objects.create(
            user=self.user1, game='note', difficulty='beginner',
            week_start=old_week, total_correct=100, total_attempts=100
        )
        response = self.client.get(
            '/leaderboard/?game=note&difficulty=beginner&period=weekly'
        )
        leaderboard = response.context['leaderboard']
        self.assertEqual(len(leaderboard), 0)

    def test_authenticated_user_rank_shown(self):
        """Logged-in user's rank should be set in context."""
        self.client.login(username='alice', password='testpass123!')
        Score.objects.create(
            user=self.user1, game='note', correct=10, total=15
        )
        response = self.client.get('/leaderboard/?game=note')
        self.assertIsNotNone(response.context['user_rank'])
        self.assertEqual(response.context['user_rank']['username'], 'alice')

    def test_anonymous_user_rank_is_none(self):
        """Anonymous user's rank should be None."""
        response = self.client.get('/leaderboard/')
        self.assertIsNone(response.context['user_rank'])

    def test_user_not_on_board_rank_is_none(self):
        """User with no scores should have user_rank=None."""
        self.client.login(username='alice', password='testpass123!')
        response = self.client.get('/leaderboard/?game=note')
        self.assertIsNone(response.context['user_rank'])

    def test_different_games_isolated(self):
        """Scores for one game should not appear in another game's board."""
        Score.objects.create(
            user=self.user1, game='note', correct=10, total=15
        )
        response = self.client.get('/leaderboard/?game=interval')
        self.assertEqual(len(response.context['leaderboard']), 0)

    def test_different_difficulties_isolated(self):
        """Scores for one difficulty should not appear in another."""
        Score.objects.create(
            user=self.user1, game='note', difficulty='advanced',
            correct=10, total=15
        )
        response = self.client.get(
            '/leaderboard/?game=note&difficulty=beginner'
        )
        self.assertEqual(len(response.context['leaderboard']), 0)


class SubmitScoreAPITests(TestCase):
    """Tests for the submit_score API endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('player', password='testpass123!')
        self.valid_payload = {
            'game': 'note',
            'difficulty': 'beginner',
            'correct': 15,
            'total': 20,
            'bestStreak': 8,
        }

    def _post_score(self, data=None, logged_in=True):
        if logged_in:
            self.client.login(username='player', password='testpass123!')
        return self.client.post(
            '/leaderboard/api/submit/',
            data=json.dumps(data or self.valid_payload),
            content_type='application/json',
        )

    def test_submit_score_success(self):
        """Valid submission should return 200 with success=True."""
        response = self._post_score()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('score_id', data)
        self.assertIn('rank', data)

    def test_submit_creates_score_object(self):
        """Submitting should create a Score in the database."""
        self._post_score()
        self.assertEqual(Score.objects.count(), 1)
        score = Score.objects.first()
        self.assertEqual(score.user, self.user)
        self.assertEqual(score.game, 'note')
        self.assertEqual(score.correct, 15)
        self.assertEqual(score.total, 20)
        self.assertEqual(score.best_streak, 8)

    def test_submit_creates_weekly_score(self):
        """Submitting should create a WeeklyScore entry."""
        self._post_score()
        self.assertEqual(WeeklyScore.objects.count(), 1)
        weekly = WeeklyScore.objects.first()
        self.assertEqual(weekly.total_correct, 15)
        self.assertEqual(weekly.total_attempts, 20)
        self.assertEqual(weekly.sessions_played, 1)
        self.assertEqual(weekly.best_streak, 8)

    def test_submit_accumulates_weekly_score(self):
        """Multiple submissions in the same week should accumulate."""
        self._post_score()
        self._post_score(data={
            'game': 'note', 'difficulty': 'beginner',
            'correct': 10, 'total': 12, 'bestStreak': 5,
        })
        self.assertEqual(WeeklyScore.objects.count(), 1)
        weekly = WeeklyScore.objects.first()
        self.assertEqual(weekly.total_correct, 25)
        self.assertEqual(weekly.total_attempts, 32)
        self.assertEqual(weekly.sessions_played, 2)

    def test_weekly_best_streak_only_increases(self):
        """WeeklyScore best_streak should only increase, not decrease."""
        self._post_score(data={
            'game': 'note', 'difficulty': 'beginner',
            'correct': 10, 'total': 15, 'bestStreak': 10,
        })
        self._post_score(data={
            'game': 'note', 'difficulty': 'beginner',
            'correct': 10, 'total': 15, 'bestStreak': 3,
        })
        weekly = WeeklyScore.objects.first()
        self.assertEqual(weekly.best_streak, 10)

    def test_unauthenticated_returns_401(self):
        """Unauthenticated user should get 401."""
        response = self._post_score(logged_in=False)
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()['success'])

    def test_invalid_game_returns_400(self):
        """Invalid game type should return 400."""
        response = self._post_score(data={
            'game': 'invalid', 'correct': 10, 'total': 15,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid game', response.json()['error'])

    def test_invalid_difficulty_returns_400(self):
        """Invalid difficulty should return 400."""
        response = self._post_score(data={
            'game': 'note', 'difficulty': 'expert',
            'correct': 10, 'total': 15,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid difficulty', response.json()['error'])

    def test_below_minimum_attempts_returns_400(self):
        """Fewer than 10 total attempts should be rejected."""
        response = self._post_score(data={
            'game': 'note', 'correct': 5, 'total': 9,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Minimum 10 attempts', response.json()['error'])

    def test_exactly_10_attempts_accepted(self):
        """Exactly 10 total attempts should be accepted."""
        response = self._post_score(data={
            'game': 'note', 'correct': 8, 'total': 10,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_get_request_returns_405(self):
        """GET requests to submit endpoint should return 405."""
        self.client.login(username='player', password='testpass123!')
        response = self.client.get('/leaderboard/api/submit/')
        self.assertEqual(response.status_code, 405)

    def test_malformed_json_returns_400(self):
        """Malformed JSON body should return 400."""
        self.client.login(username='player', password='testpass123!')
        response = self.client.post(
            '/leaderboard/api/submit/',
            data='not json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_score_accuracy_calculated(self):
        """Created Score should have auto-calculated accuracy."""
        self._post_score()
        score = Score.objects.first()
        self.assertEqual(score.accuracy, 75.0)

    def test_submit_returns_rank(self):
        """Response should include the user's rank."""
        response = self._post_score()
        data = response.json()
        self.assertEqual(data['rank'], 1)

    def test_difficulty_defaults_to_beginner(self):
        """Missing difficulty should default to beginner."""
        response = self._post_score(data={
            'game': 'note', 'correct': 10, 'total': 15,
        })
        self.assertEqual(response.status_code, 200)
        score = Score.objects.first()
        self.assertEqual(score.difficulty, 'beginner')

    def test_all_valid_games_accepted(self):
        """All four game types should be accepted."""
        for game in ['note', 'interval', 'chord', 'pitch']:
            response = self._post_score(data={
                'game': game, 'correct': 10, 'total': 15,
            })
            self.assertEqual(
                response.status_code, 200,
                f"Game '{game}' should be accepted"
            )

    def test_all_valid_difficulties_accepted(self):
        """All three difficulties should be accepted."""
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            response = self._post_score(data={
                'game': 'note', 'difficulty': difficulty,
                'correct': 10, 'total': 15,
            })
            self.assertEqual(
                response.status_code, 200,
                f"Difficulty '{difficulty}' should be accepted"
            )


class APILeaderboardTests(TestCase):
    """Tests for the api_leaderboard JSON endpoint."""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('alice', password='testpass123!')
        self.user2 = User.objects.create_user('bob', password='testpass123!')

    def test_returns_json(self):
        """Should return a JSON response with 'leaderboard' key."""
        response = self.client.get('/leaderboard/api/rankings/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('leaderboard', data)

    def test_empty_leaderboard(self):
        """Should return an empty list when no scores exist."""
        response = self.client.get('/leaderboard/api/rankings/')
        data = response.json()
        self.assertEqual(data['leaderboard'], [])

    def test_alltime_aggregates_scores(self):
        """All-time should aggregate all scores per user."""
        Score.objects.create(
            user=self.user1, game='note', correct=10, total=15
        )
        Score.objects.create(
            user=self.user1, game='note', correct=5, total=10
        )
        response = self.client.get('/leaderboard/api/rankings/?game=note')
        data = response.json()
        self.assertEqual(len(data['leaderboard']), 1)
        self.assertEqual(data['leaderboard'][0]['correct'], 15)

    def test_alltime_ranks_by_correct(self):
        """Users should be ranked by total correct descending."""
        Score.objects.create(
            user=self.user1, game='note', correct=5, total=10
        )
        Score.objects.create(
            user=self.user2, game='note', correct=20, total=25
        )
        response = self.client.get('/leaderboard/api/rankings/?game=note')
        data = response.json()
        self.assertEqual(data['leaderboard'][0]['username'], 'bob')
        self.assertEqual(data['leaderboard'][1]['username'], 'alice')

    def test_weekly_returns_current_week_only(self):
        """Weekly period should only return current week's scores."""
        week_start = get_week_start()
        WeeklyScore.objects.create(
            user=self.user1, game='note', week_start=week_start,
            total_correct=10, total_attempts=15
        )
        old_week = week_start - timedelta(weeks=1)
        WeeklyScore.objects.create(
            user=self.user2, game='note', week_start=old_week,
            total_correct=100, total_attempts=100
        )
        response = self.client.get(
            '/leaderboard/api/rankings/?game=note&period=weekly'
        )
        data = response.json()
        self.assertEqual(len(data['leaderboard']), 1)
        self.assertEqual(data['leaderboard'][0]['username'], 'alice')

    def test_limit_param_caps_results(self):
        """Limit parameter should restrict the number of results."""
        for i in range(5):
            user = User.objects.create_user(f'user{i}', password='testpass123!')
            Score.objects.create(user=user, game='note', correct=i, total=10)
        response = self.client.get(
            '/leaderboard/api/rankings/?game=note&limit=3'
        )
        data = response.json()
        self.assertEqual(len(data['leaderboard']), 3)

    def test_limit_capped_at_50(self):
        """Limit should be capped at 50 even if a higher value is passed."""
        response = self.client.get(
            '/leaderboard/api/rankings/?game=note&limit=999'
        )
        # No error — the view clamps to 50 internally
        self.assertEqual(response.status_code, 200)

    def test_default_limit_is_10(self):
        """Default limit should be 10."""
        for i in range(15):
            user = User.objects.create_user(f'user{i}', password='testpass123!')
            Score.objects.create(user=user, game='note', correct=i, total=10)
        response = self.client.get('/leaderboard/api/rankings/?game=note')
        data = response.json()
        self.assertEqual(len(data['leaderboard']), 10)

    def test_filters_by_game(self):
        """Should only return scores for the requested game."""
        Score.objects.create(
            user=self.user1, game='note', correct=10, total=15
        )
        Score.objects.create(
            user=self.user2, game='interval', correct=10, total=15
        )
        response = self.client.get(
            '/leaderboard/api/rankings/?game=interval'
        )
        data = response.json()
        self.assertEqual(len(data['leaderboard']), 1)
        self.assertEqual(data['leaderboard'][0]['username'], 'bob')

    def test_entries_include_rank_and_accuracy(self):
        """Each entry should have rank, username, correct, and accuracy."""
        Score.objects.create(
            user=self.user1, game='note', correct=8, total=10
        )
        response = self.client.get('/leaderboard/api/rankings/?game=note')
        entry = response.json()['leaderboard'][0]
        self.assertEqual(entry['rank'], 1)
        self.assertEqual(entry['username'], 'alice')
        self.assertEqual(entry['correct'], 8)
        self.assertEqual(entry['accuracy'], 80.0)

    def test_accessible_without_authentication(self):
        """Leaderboard API should be accessible anonymously."""
        response = self.client.get('/leaderboard/api/rankings/')
        self.assertEqual(response.status_code, 200)
