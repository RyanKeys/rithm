from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.views import generic, View
from datetime import datetime
from .models import Game


class IndexView(generic.ListView):
    template_name = 'landing_page/index.html'
    model = Game

    def get(self, request):
        games = self.get_queryset().all()
        return render(request, self.template_name, {"games": games})


class ShowTimeView(View):

    def get(self, request):
        now = datetime.now()
        html = f"<html>It is now {now}. </html>"
        return HttpResponse(html)


def music_theory_guide(request):
    """Music Theory Guide page."""
    return render(request, 'landing_page/guide.html')


def practice_tips(request):
    """Practice Tips page."""
    return render(request, 'landing_page/tips.html')


def faq(request):
    """FAQ page."""
    return render(request, 'landing_page/faq.html')
