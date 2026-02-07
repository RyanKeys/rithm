from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid


class EmailVerification(models.Model):
    """Store email verification tokens for new users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def is_expired(self):
        """Token expires after 24 hours."""
        expiry = self.created_at + timezone.timedelta(hours=24)
        return timezone.now() > expiry
    
    def verify(self):
        """Mark email as verified."""
        self.verified_at = timezone.now()
        self.save()
        # Activate the user
        self.user.is_active = True
        self.user.save()
    
    def __str__(self):
        return f"Verification for {self.user.email}"


class UserProfile(models.Model):
    """Extended user profile for storing game progress and preferences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Note Identification Stats
    note_total_correct = models.IntegerField(default=0)
    note_total_attempts = models.IntegerField(default=0)
    note_best_streak = models.IntegerField(default=0)
    note_current_streak = models.IntegerField(default=0)
    note_difficulty = models.CharField(max_length=20, default='beginner')
    
    # Pitch Identification Stats
    pitch_total_correct = models.IntegerField(default=0)
    pitch_total_attempts = models.IntegerField(default=0)
    pitch_best_streak = models.IntegerField(default=0)
    
    # Interval Training Stats
    interval_total_correct = models.IntegerField(default=0)
    interval_total_attempts = models.IntegerField(default=0)
    interval_best_streak = models.IntegerField(default=0)
    interval_current_streak = models.IntegerField(default=0)
    interval_difficulty = models.CharField(max_length=20, default='beginner')

    # Chord Identification Stats
    chord_total_correct = models.IntegerField(default=0)
    chord_total_attempts = models.IntegerField(default=0)
    chord_best_streak = models.IntegerField(default=0)
    chord_current_streak = models.IntegerField(default=0)
    chord_difficulty = models.CharField(max_length=20, default='beginner')

    # General
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def note_accuracy(self):
        if self.note_total_attempts == 0:
            return 0
        return round((self.note_total_correct / self.note_total_attempts) * 100)
    
    @property
    def pitch_accuracy(self):
        if self.pitch_total_attempts == 0:
            return 0
        return round((self.pitch_total_correct / self.pitch_total_attempts) * 100)
    
    @property
    def interval_accuracy(self):
        if self.interval_total_attempts == 0:
            return 0
        return round((self.interval_total_correct / self.interval_total_attempts) * 100)

    @property
    def chord_accuracy(self):
        if self.chord_total_attempts == 0:
            return 0
        return round((self.chord_total_correct / self.chord_total_attempts) * 100)


# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
