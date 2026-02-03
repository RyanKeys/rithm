from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Max, Count
from django.utils import timezone
from datetime import timedelta
from .models import Score, WeeklyScore
import json


def get_week_start(date=None):
    """Get Monday of the current week."""
    if date is None:
        date = timezone.now().date()
    return date - timedelta(days=date.weekday())


def leaderboard_view(request):
    """Main leaderboard page."""
    game = request.GET.get('game', 'note')
    difficulty = request.GET.get('difficulty', 'beginner')
    period = request.GET.get('period', 'alltime')
    
    games = [
        {'id': 'note', 'name': 'Note Reading', 'icon': 'fa-book-open'},
        {'id': 'interval', 'name': 'Interval Training', 'icon': 'fa-music'},
        {'id': 'chord', 'name': 'Chord Identification', 'icon': 'fa-layer-group'},
        {'id': 'pitch', 'name': 'Pitch Identification', 'icon': 'fa-headphones'},
    ]
    
    difficulties = [
        {'id': 'beginner', 'name': 'Beginner', 'icon': 'fa-seedling'},
        {'id': 'intermediate', 'name': 'Intermediate', 'icon': 'fa-leaf'},
        {'id': 'advanced', 'name': 'Advanced', 'icon': 'fa-tree'},
    ]
    
    if period == 'weekly':
        week_start = get_week_start()
        leaders = WeeklyScore.objects.filter(
            game=game,
            difficulty=difficulty,
            week_start=week_start
        ).select_related('user').order_by('-total_correct', '-accuracy')[:50]
        
        leaderboard_data = [{
            'rank': i + 1,
            'username': score.user.username,
            'correct': score.total_correct,
            'accuracy': score.accuracy,
            'best_streak': score.best_streak,
            'sessions': score.sessions_played,
        } for i, score in enumerate(leaders)]
    else:
        # All-time: aggregate all scores per user
        from django.contrib.auth.models import User
        
        leaders = Score.objects.filter(game=game, difficulty=difficulty).values('user__username').annotate(
            total_correct=Sum('correct'),
            total_attempts=Sum('total'),
            max_streak=Max('best_streak'),
            sessions=Count('id')
        ).order_by('-total_correct')[:50]
        
        leaderboard_data = [{
            'rank': i + 1,
            'username': leader['user__username'],
            'correct': leader['total_correct'],
            'accuracy': round((leader['total_correct'] / leader['total_attempts'] * 100), 1) if leader['total_attempts'] > 0 else 0,
            'best_streak': leader['max_streak'],
            'sessions': leader['sessions'],
        } for i, leader in enumerate(leaders)]
    
    # Get current user's rank
    user_rank = None
    if request.user.is_authenticated:
        for entry in leaderboard_data:
            if entry['username'] == request.user.username:
                user_rank = entry
                break
    
    context = {
        'games': games,
        'difficulties': difficulties,
        'current_game': game,
        'current_difficulty': difficulty,
        'period': period,
        'leaderboard': leaderboard_data,
        'user_rank': user_rank,
    }
    
    return render(request, 'leaderboard/index.html', context)


@require_POST
def submit_score(request):
    """API endpoint to submit a game score."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    try:
        data = json.loads(request.body)
        game = data.get('game')
        difficulty = data.get('difficulty', 'beginner')
        correct = data.get('correct', 0)
        total = data.get('total', 0)
        best_streak = data.get('bestStreak', 0)
        
        if game not in ['note', 'interval', 'chord', 'pitch']:
            return JsonResponse({'success': False, 'error': 'Invalid game'}, status=400)
        
        if difficulty not in ['beginner', 'intermediate', 'advanced']:
            return JsonResponse({'success': False, 'error': 'Invalid difficulty'}, status=400)
        
        if total < 10:
            return JsonResponse({'success': False, 'error': 'Minimum 10 attempts required'}, status=400)
        
        # Create score entry
        score = Score.objects.create(
            user=request.user,
            game=game,
            difficulty=difficulty,
            correct=correct,
            total=total,
            best_streak=best_streak
        )
        
        # Update weekly score
        week_start = get_week_start()
        weekly, created = WeeklyScore.objects.get_or_create(
            user=request.user,
            game=game,
            difficulty=difficulty,
            week_start=week_start,
            defaults={
                'total_correct': 0,
                'total_attempts': 0,
                'best_streak': 0,
                'sessions_played': 0
            }
        )
        
        weekly.total_correct += correct
        weekly.total_attempts += total
        weekly.sessions_played += 1
        if best_streak > weekly.best_streak:
            weekly.best_streak = best_streak
        weekly.save()
        
        # Get user's current rank for this game + difficulty
        rank = Score.objects.filter(game=game, difficulty=difficulty).values('user').annotate(
            total=Sum('correct')
        ).filter(total__gt=Score.objects.filter(game=game, difficulty=difficulty, user=request.user).aggregate(Sum('correct'))['correct__sum'] or 0).count() + 1
        
        return JsonResponse({
            'success': True,
            'score_id': score.id,
            'rank': rank,
            'difficulty': difficulty
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def api_leaderboard(request):
    """API endpoint to get leaderboard data."""
    game = request.GET.get('game', 'note')
    period = request.GET.get('period', 'alltime')
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    if period == 'weekly':
        week_start = get_week_start()
        leaders = WeeklyScore.objects.filter(
            game=game,
            week_start=week_start
        ).select_related('user').order_by('-total_correct', '-accuracy')[:limit]
        
        data = [{
            'rank': i + 1,
            'username': score.user.username,
            'correct': score.total_correct,
            'accuracy': score.accuracy,
        } for i, score in enumerate(leaders)]
    else:
        leaders = Score.objects.filter(game=game).values('user__username').annotate(
            total_correct=Sum('correct'),
            total_attempts=Sum('total'),
        ).order_by('-total_correct')[:limit]
        
        data = [{
            'rank': i + 1,
            'username': leader['user__username'],
            'correct': leader['total_correct'],
            'accuracy': round((leader['total_correct'] / leader['total_attempts'] * 100), 1) if leader['total_attempts'] > 0 else 0,
        } for i, leader in enumerate(leaders)]
    
    return JsonResponse({'leaderboard': data})
