"""iwdsync/vies.py
"""
from django.http import HttpResponse


def home(request):
    return HttpResponse('welcome home')


def loader(request):
    return HttpResponse('loaderio-7b256fbe6d3910eaba847ceba38a7cb7')
