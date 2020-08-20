from django.urls import re_path

from . import consumers

urlpatterns = [
    re_path('ws/viewer/(?P<caster>\w+)/?$', consumers.ViewerConsumer),
    re_path('ws/caster/(?P<caster>\w+)/?$', consumers.CasterConsumer)
]
