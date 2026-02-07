from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Email verification
    path('verify/<uuid:token>/', views.verify_email, name='verify-email'),
    path('resend-verification/', views.resend_verification, name='resend-verification'),
    
    # API endpoints for game stats
    path('api/note-stats/', views.get_note_stats, name='get-note-stats'),
    path('api/note-stats/update/', views.update_note_stats, name='update-note-stats'),
    path('api/interval-stats/', views.get_interval_stats, name='get-interval-stats'),
    path('api/interval-stats/update/', views.update_interval_stats, name='update-interval-stats'),
    path('api/chord-stats/', views.get_chord_stats, name='get-chord-stats'),
    path('api/chord-stats/update/', views.update_chord_stats, name='update-chord-stats'),
]
