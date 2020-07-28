"""caster/viewsapi.py
"""
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

from caster.models import Caster
from caster.serializers import CasterSerializer


@csrf_exempt
@api_view(["GET", "PUT", "POST"])
def caster(request, format=None):
    """Get, update, create caster models
    """
    if request.method == "GET":
        data, status_code = get_caster(request)
    elif request.method == "POST":
        action = request.data.get("action")
        if action == "update":
            data, status_code = update_caster(request)
        elif action == "create":
            pass
    return Response(data, status=status_code, headers=get_headers(request))


def get_headers(request):
    token = get_token(request)
    headers = {'Set-Cookie': f'csrftoken={token}'}
    return headers


def update_caster(request):
    """Update caster data.
    """
    youtube_url = request.data.get("youtube_url")
    irl_time = request.data.get("irl_time")
    youtube_time = request.data.get("youtube_time")
    if request.user.is_authenticated:
        caster = request.user.caster
        if youtube_url is not None:
            caster.youtube_url = youtube_url
        if irl_time is not None:
            caster.irl_time = irl_time
        if youtube_time is not None:
            caster.youtube_time = youtube_time
        caster.save()
        data = {"message": "updated caster data"}
        status_code = 200
    else:
        data = {"status": "not_logged_in", "message": "not logged in"}
        status_code = 403
    return data, status_code


def get_caster(request):
    """Retrieve a caster.

    Parameters
    ----------
    url_path : str

    Returns
    -------
    dict, int

    """
    url_path = request.GET["url_path"]
    query = Caster.objects.filter(url_path=url_path)
    data = {}
    status_code = 200
    if query.exists():
        caster = query.first()
        data = {"data": CasterSerializer(caster, many=False).data}
    return data, status_code


@api_view(["GET"])
def get_my_caster(request, format=None):
    """Get a user's connected caster."""
    data = {}
    status_code = 200
    if request.user.is_authenticated:
        caster = request.user.caster
        data = {"data": CasterSerializer(caster, many=False).data}
    else:
        data = {"message": "Not authenticated."}
        status_code = 403
    return Response(data, status=status_code)


@api_view(['GET'])
def get_csrf(request, format=None):
    token = get_token(request)
    data = {"data": token}
    return Response(data, headers=get_headers(request))
