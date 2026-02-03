from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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


# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
