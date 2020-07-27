"""iwdsync/vies.py
"""
from django.http import HttpResponse


def home(request):
    return HttpResponse('welcome home')
