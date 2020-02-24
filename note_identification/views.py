from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.views import generic, View
from datetime import datetime
# from .models import Game


class IndexView(generic.ListView):
    template_name = 'note_identification/index.html'

    def get(self, request):
        return render(request, self.template_name)
