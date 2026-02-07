from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .forms import RegistrationForm
from .models import EmailVerification
import json


def send_verification_email(user, request):
    """Send email verification link to user."""
    # Create or get verification token
    verification, created = EmailVerification.objects.get_or_create(user=user)
    if not created:
        # Reset token if resending
        import uuid
        verification.token = uuid.uuid4()
        verification.save()
    
    # Build verification URL
    verification_url = request.build_absolute_uri(f'/accounts/verify/{verification.token}/')
    
    # Render email
    html_message = render_to_string('accounts/email/verify_email.html', {
        'user': user,
        'verification_url': verification_url,
    })
    plain_message = strip_tags(html_message)
    
    # Send email
    try:
        send_mail(
            subject='Verify your R.I.T.H.M account',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False


def register_view(request):
    """Handle user registration with email verification."""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create user but set inactive until email verified
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Send verification email
            if send_verification_email(user, request):
                messages.success(
                    request, 
                    f'Account created! Please check {user.email} to verify your email address.'
                )
                return render(request, 'accounts/verification_sent.html', {'email': user.email})
            else:
                # If email fails, still create account but warn user
                user.is_active = True
                user.save()
                login(request, user)
                messages.warning(
                    request, 
                    'Account created, but we could not send a verification email. Please contact support.'
                )
                return redirect('/')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def verify_email(request, token):
    """Handle email verification link."""
    try:
        verification = get_object_or_404(EmailVerification, token=token)
        
        if verification.verified_at:
            messages.info(request, 'Your email has already been verified. Please log in.')
            return redirect('login')
        
        if verification.is_expired():
            messages.error(request, 'This verification link has expired. Please register again.')
            # Delete the unverified user
            verification.user.delete()
            return redirect('register')
        
        # Verify the email
        verification.verify()
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('login')
        
    except Exception as e:
        messages.error(request, 'Invalid verification link.')
        return redirect('register')


def resend_verification(request):
    """Resend verification email."""
    if request.method == 'POST':
        email = request.POST.get('email')
        from django.contrib.auth.models import User
        
        try:
            user = User.objects.get(email=email, is_active=False)
            if send_verification_email(user, request):
                messages.success(request, f'Verification email sent to {email}')
            else:
                messages.error(request, 'Failed to send verification email. Please try again.')
        except User.DoesNotExist:
            # Don't reveal if email exists
            messages.info(request, 'If that email is registered, you will receive a verification link.')
        
        return render(request, 'accounts/verification_sent.html', {'email': email})
    
    return render(request, 'accounts/resend_verification.html')


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


@require_POST
def update_chord_stats(request):
    """API endpoint to update chord identification stats."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

    try:
        data = json.loads(request.body)
        profile = request.user.profile

        # Update stats
        if 'correct' in data:
            profile.chord_total_correct = data['correct']
        if 'total' in data:
            profile.chord_total_attempts = data['total']
        if 'streak' in data:
            profile.chord_current_streak = data['streak']
        if 'bestStreak' in data:
            if data['bestStreak'] > profile.chord_best_streak:
                profile.chord_best_streak = data['bestStreak']
        if 'difficulty' in data:
            profile.chord_difficulty = data['difficulty']

        profile.save()

        return JsonResponse({
            'success': True,
            'stats': {
                'correct': profile.chord_total_correct,
                'total': profile.chord_total_attempts,
                'streak': profile.chord_current_streak,
                'bestStreak': profile.chord_best_streak,
                'accuracy': profile.chord_accuracy,
                'difficulty': profile.chord_difficulty
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def get_chord_stats(request):
    """API endpoint to get chord identification stats."""
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False})

    profile = request.user.profile
    return JsonResponse({
        'authenticated': True,
        'stats': {
            'correct': profile.chord_total_correct,
            'total': profile.chord_total_attempts,
            'streak': profile.chord_current_streak,
            'bestStreak': profile.chord_best_streak,
            'accuracy': profile.chord_accuracy,
            'difficulty': profile.chord_difficulty
        }
    })
