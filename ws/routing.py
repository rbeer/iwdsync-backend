from django.urls import re_path

from . import consumers

urlpatterns = [
    re_path('ws/(?P<caster>\w+)/?$', consumers.ViewerConsumer)
]
