from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Note migration test view!")
# Create your views here.
