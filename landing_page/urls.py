from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view()),
    path("now/", views.ShowTimeView.as_view()),
]
