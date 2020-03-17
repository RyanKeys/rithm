from django.urls import path

from . import views
from note_identification import views as note_views
from pitch_identification import views as pitch_views

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('note_identification/', note_views.IndexView.as_view(),
         name="note_identification"),
    path('pitch_identification/', pitch_views.IndexView.as_view(),
         name="pitch_identification"),
]
