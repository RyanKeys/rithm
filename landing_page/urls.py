from django.urls import path

from . import views
from note_identification import views as note_views
from pitch_identification import views as pitch_views
from synth import views as synth_views

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('note_identification/', note_views.IndexView.as_view(),
         name="note_identification"),
    path('pitch_identification/', pitch_views.IndexView.as_view(),
         name="pitch_identification"),
    path('synth/', synth_views.IndexView.as_view(), name="synth"),
    
    # Content pages
    path('guide/', views.music_theory_guide, name="guide"),
    path('tips/', views.practice_tips, name="tips"),
    path('faq/', views.faq, name="faq"),
]
