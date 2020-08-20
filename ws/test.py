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
    assert response == { 'youtube_time': 99.09 }

    # receives control commands
    await channel_layer.group_send('iwd', {
        'type': 'control',
        'action': 'play'
    })
    response = await communicator.receive_json_from()
    assert response == { 'control': 'play' }

    await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_caster_consumer():
    user = await sta(User.objects.create)(username='test_user')

    # test failure when not logged in
    communicator = await connect('/ws/caster/iwd')
    response = await communicator.receive_json_from()
    assert response == {'status': 'error', 'message': 'Not authenticated.'}
    await communicator.disconnect()

    # authroized, from now on
    communicator = await connect('/ws/caster/iwd', user=user)
    assert await communicator.receive_nothing() == True

    # returns error when no `url_path` is given
    await communicator.send_json_to({ 'hello': True })
    response = await communicator.receive_json_from()
    assert response == {
        'status': 'error',
        'message': 'url_path must be a string.'
    }

    # returns error when no `time` is given
    await communicator.send_json_to({ 'url_path': 'iwd' })
    response = await communicator.receive_json_from()
    assert response == {
        'status': 'error',
        'message': 'time must be a number.'
    }

    # return error when logged in user is not assigned to user from `url_path`
    await communicator.send_json_to({ 'url_path': 'iwd', 'time': 100.010 })
    response = await communicator.receive_json_from()
    assert response == {
        'status': 'error',
        'message': 'No caster found.'
    }

    # returns `ok` and updates Caster with new `yotube_time`
    caster = await sta(Caster.objects.create)(
        user=user,
        twitch_channel='iwilldominate',
        url_path='iwd',
        youtube_url='https://you.tube/?v=0sSi2ja2',
        youtube_time=200.100,
        irl_time=0.1
    )
    await sta(caster.save)()
    await communicator.send_json_to({ 'url_path': 'iwd', 'time': 100.010 })
    response = await communicator.receive_json_from()
    assert response == { 'status': 'ok' }
    caster = await sta(Caster.objects.get)(user=user)
    assert caster.youtube_time == 100.010

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
