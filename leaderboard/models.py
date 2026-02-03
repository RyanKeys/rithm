from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Score(models.Model):
    """Individual game score entry for leaderboards."""
    
    GAME_CHOICES = [
        ('note', 'Note Reading'),
        ('interval', 'Interval Training'),
        ('chord', 'Chord Identification'),
        ('pitch', 'Pitch Identification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    game = models.CharField(max_length=20, choices=GAME_CHOICES)
    
    # Score metrics
    correct = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    
    # Calculated on save
    accuracy = models.FloatField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-correct', '-accuracy', '-best_streak']
        indexes = [
            models.Index(fields=['game', '-correct']),
            models.Index(fields=['game', 'created_at']),
        ]
    
    def save(self, *args, **kwargs):
        # Calculate accuracy before saving
        if self.total > 0:
            self.accuracy = round((self.correct / self.total) * 100, 1)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.game}: {self.correct} correct ({self.accuracy}%)"


class WeeklyScore(models.Model):
    """Aggregated weekly scores for weekly leaderboards."""
    
    GAME_CHOICES = Score.GAME_CHOICES
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_scores')
    game = models.CharField(max_length=20, choices=GAME_CHOICES)
    
    # Week identifier (Monday of the week)
    week_start = models.DateField()
    
    # Aggregated metrics
    total_correct = models.IntegerField(default=0)
    total_attempts = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    sessions_played = models.IntegerField(default=0)
    
    # Calculated
    accuracy = models.FloatField(default=0)
    
    class Meta:
        unique_together = ['user', 'game', 'week_start']
        ordering = ['-total_correct', '-accuracy']
        indexes = [
            models.Index(fields=['game', 'week_start', '-total_correct']),
        ]
    
    def save(self, *args, **kwargs):
        if self.total_attempts > 0:
            self.accuracy = round((self.total_correct / self.total_attempts) * 100, 1)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.game} (week of {self.week_start}): {self.total_correct}"
