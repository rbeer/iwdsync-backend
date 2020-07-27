"""caster/viewsapi.py
"""
from rest_framework.response import Response
from rest_framework.decorators import api_view

from caster.models import Caster
from caster.serializers import CasterSerializer


@api_view(["GET", "PUT", "POST"])
def caster(request, format=None):
    """
    """
    print(request.user)
    if request.method == "GET":
        data, status_code = get_caster(request)
    elif request.method == "PUT":
        data, status_code = update_caster()
    elif request.method == "POST":
        pass
    return Response(data, status=status_code)


def get_caster(request):
    """Retrieve a caster.

    Parameters
    ----------
    url_path : str

    Returns
    -------
    dict, int

    """
    url_path = request.GET['url_path']
    query = Caster.objects.filter(url_path=url_path)
    data = {}
    status_code = 200
    if query.exists():
        caster = query.first()
        data = {'data': CasterSerializer(caster, many=False).data}
    return data, status_code


@api_view(['GET'])
def get_my_caster(request, format=None):
    """Get a user's connected caster."""
    data = {}
    status_code = 200
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        caster = request.user.caster
        data = {'data': CasterSerializer(caster, many=False).data}
    else:
        data = {'message': 'Not authenticated.'}
        status_code = 404
    return Response(data, status=status_code)
