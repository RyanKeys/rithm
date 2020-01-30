from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.views import generic
from .models import Game


class IndexView(generic.ListView):
    template_name = 'index.html'
    model = Game

    def get(self, request):
        games = self.get_queryset().all()
        return render(request, "index.html", {"games": games})
