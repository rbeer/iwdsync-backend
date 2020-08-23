import pytest
from asgiref.sync import sync_to_async as sta
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User

from caster.models import Caster
from iwdsync.asgi import application

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_viewer_consumer():
    communicator = await connect('/ws/viewer/iwd')
    assert await communicator.receive_nothing() == True

    # connecting adds client to /ws/viewer/{caster}'s channel group
    channel_layer = get_channel_layer()
    assert channel_layer.groups.get('iwd', None) != None

    # receives udated youtube_time
    await channel_layer.group_send('iwd', {
        'type': 'heartbeat',
        'youtube_time': 99.09
    })
    response = await communicator.receive_json_from()
    assert response == { 'type': 'HEARTBEAT', 'youtube_time': 99.09 }

    # receives control commands
    await channel_layer.group_send('iwd', {
        'type': 'control',
        'action': 'play'
    })
    response = await communicator.receive_json_from()
    assert response == { 'type': 'CONTROL', 'action': 'play' }

    await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_caster_connect():
    user = await sta(User.objects.create)(username='caster_connect_user')
    communicator = await connect('/ws/caster/caster_connect')

    # returns error and closes connection when not logged in
    response = await communicator.receive_json_from()
    assert response == { 'status': 'error', 'message': 'Not authenticated.' }

    # returns error when authenticated user has no caster
    communicator = await connect('/ws/caster/caster_connect', user=user)
    response = await communicator.receive_json_from()
    assert response == { 'status': 'error', 'message': 'No caster found.' }
    await communicator.disconnect()

    caster = await sta(Caster.objects.create)(
        user=user,
        twitch_channel='caster_connect',
        url_path='caster_connect',
        youtube_url='https://you.tube/?v=0sSi2ja2',
        youtube_time=200.100,
        irl_time=0.1
    )

    communicator = await connect('/ws/caster/caster_connect', user=user)
    # returns error when no `type` is given
    await communicator.send_json_to({ 'hello': True })
    response = await communicator.receive_json_from()
    assert response == {
        'status': 'error',
        'message': "type must be one of ['HEARTBEAT', 'CONTROL']"
    }

    await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_caster_heartbeat():
    user = await sta(User.objects.create)(username='caster_heartbeat_user')
    caster = await sta(Caster.objects.create)(
        user=user,
        twitch_channel='caster_heartbeat',
        url_path='caster_heartbeat',
        youtube_url='https://you.tube/?v=0sSi2ja2',
        youtube_time=200.100,
        irl_time=0.1
    )
    communicator = await connect('/ws/caster/caster_heartbeat', user=user)
    viewer_communicator = await connect('/ws/viewer/caster_heartbeat')

    # HEARTBEAT returns error when no `time` is given
    await communicator.send_json_to({
        'type': 'HEARTBEAT',
    })
    response = await communicator.receive_json_from()
    assert response == {
        'status': 'error',
        'message': 'youtube_time must be a number.'
    }

    # updates Caster with new `yotube_time`, ...
    await communicator.send_json_to({
        'type': 'HEARTBEAT',
        'youtube_time': 100.010
    })
    response = await communicator.receive_json_from()

    caster = await sta(Caster.objects.get)(user=user)
    assert caster.youtube_time == 100.010

    # ... responds with 'ok'
    assert response == { 'status': 'ok' }

    # and sends new 'youtube_time' to viewers
    response = await viewer_communicator.receive_json_from()
    assert response == { 'type': 'HEARTBEAT', 'youtube_time': 100.010 }

    await viewer_communicator.disconnect()
    await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_caster_control():
    user = await sta(User.objects.create)(username='caster_control_user')
    caster = await sta(Caster.objects.create)(
        user=user,
        twitch_channel='caster_control',
        url_path='caster_control',
        youtube_url='https://you.tube/?v=0sSi2ja2',
        youtube_time=200.100,
        irl_time=0.1
    )
    communicator = await connect('/ws/caster/caster_control', user=user)
    viewer_communicator = await connect('/ws/viewer/caster_control')

    # HEARTBEAT returns error when no `action` is given
    await communicator.send_json_to({
        'type': 'CONTROL',
    })
    response = await communicator.receive_json_from()
    assert response == {
        'status': 'error',
        'message': "action must be one of ['PLAY', 'PAUSE']"
    }

    # relays control action to viewers
    await communicator.send_json_to({
        'type': 'CONTROL',
        'action': 'PLAY'
    })
    # response = await communicator.receive_json_from()

    response = await viewer_communicator.receive_json_from()
    assert response == { 'type': 'CONTROL', 'action': 'PLAY' }

    await viewer_communicator.disconnect()
    await communicator.disconnect()

async def connect(path: str, user: User = None) -> WebsocketCommunicator:
    # use full application, instead of just the tested Consumer;
    # scope is not populated with result of re_path, otherwise
    communicator = WebsocketCommunicator(application, path)
    if user != None:
        communicator.scope['user'] = user
    connected, subprotocol = await communicator.connect()
    assert connected

    return communicator
