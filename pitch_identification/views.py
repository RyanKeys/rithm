from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.views import generic, View
from datetime import datetime
# Create your views here.


class IndexView(generic.ListView):
    template_name = 'pitch_identification/index.html'

    def get(self, request):
        return render(request, self.template_name)
