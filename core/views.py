from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'home.html')


def receive(request):
    return render(request, 'info.html')


def give(request):
    return render(request, 'info.html')
