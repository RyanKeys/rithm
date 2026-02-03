from django.urls import path
from . import views

urlpatterns = [
    path('', views.leaderboard_view, name='leaderboard'),
    path('api/submit/', views.submit_score, name='submit-score'),
    path('api/rankings/', views.api_leaderboard, name='api-leaderboard'),
]
