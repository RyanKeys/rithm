from django.contrib import admin
from .models import Score, WeeklyScore


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'correct', 'total', 'accuracy', 'best_streak', 'created_at']
    list_filter = ['game', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['accuracy', 'created_at']
    ordering = ['-created_at']


@admin.register(WeeklyScore)
class WeeklyScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'week_start', 'total_correct', 'total_attempts', 'accuracy', 'sessions_played']
    list_filter = ['game', 'week_start']
    search_fields = ['user__username']
    readonly_fields = ['accuracy']
    ordering = ['-week_start', 'game']
