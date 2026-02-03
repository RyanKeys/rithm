from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to R.I.T.H.M, {user.username}!')
            return redirect('/')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('/')


@login_required
def profile_view(request):
    """Display user profile with stats."""
    return render(request, 'accounts/profile.html', {
        'profile': request.user.profile
    })


@require_POST
def update_note_stats(request):
    """API endpoint to update note identification stats."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    try:
        data = json.loads(request.body)
        profile = request.user.profile
        
        # Update stats
        if 'correct' in data:
            profile.note_total_correct = data['correct']
        if 'total' in data:
            profile.note_total_attempts = data['total']
        if 'streak' in data:
            profile.note_current_streak = data['streak']
        if 'bestStreak' in data:
            if data['bestStreak'] > profile.note_best_streak:
                profile.note_best_streak = data['bestStreak']
        if 'difficulty' in data:
            profile.note_difficulty = data['difficulty']
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'correct': profile.note_total_correct,
                'total': profile.note_total_attempts,
                'streak': profile.note_current_streak,
                'bestStreak': profile.note_best_streak,
                'accuracy': profile.note_accuracy,
                'difficulty': profile.note_difficulty
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def get_note_stats(request):
    """API endpoint to get note identification stats."""
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False})
    
    profile = request.user.profile
    return JsonResponse({
        'authenticated': True,
        'stats': {
            'correct': profile.note_total_correct,
            'total': profile.note_total_attempts,
            'streak': profile.note_current_streak,
            'bestStreak': profile.note_best_streak,
            'accuracy': profile.note_accuracy,
            'difficulty': profile.note_difficulty
        }
    })


@require_POST
def update_interval_stats(request):
    """API endpoint to update interval training stats."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    try:
        data = json.loads(request.body)
        profile = request.user.profile
        
        # Update stats
        if 'correct' in data:
            profile.interval_total_correct = data['correct']
        if 'total' in data:
            profile.interval_total_attempts = data['total']
        if 'streak' in data:
            profile.interval_current_streak = data['streak']
        if 'bestStreak' in data:
            if data['bestStreak'] > profile.interval_best_streak:
                profile.interval_best_streak = data['bestStreak']
        if 'difficulty' in data:
            profile.interval_difficulty = data['difficulty']
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'correct': profile.interval_total_correct,
                'total': profile.interval_total_attempts,
                'streak': profile.interval_current_streak,
                'bestStreak': profile.interval_best_streak,
                'accuracy': profile.interval_accuracy,
                'difficulty': profile.interval_difficulty
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def get_interval_stats(request):
    """API endpoint to get interval training stats."""
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False})
    
    profile = request.user.profile
    return JsonResponse({
        'authenticated': True,
        'stats': {
            'correct': profile.interval_total_correct,
            'total': profile.interval_total_attempts,
            'streak': profile.interval_current_streak,
            'bestStreak': profile.interval_best_streak,
            'accuracy': profile.interval_accuracy,
            'difficulty': profile.interval_difficulty
        }
    })
