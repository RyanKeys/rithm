from django.shortcuts import render
from django.views.generic import ListView


class IndexView(ListView):
    # Create your views here.
    template_name = 'synth/index.html'

    def get(self, request):

        return render(request, self.template_name)
