from enum import Enum
import json
from asgiref.sync import sync_to_async as sta
from channels.auth import get_user
from channels.generic.websocket import AsyncWebsocketConsumer

from caster.models import Caster

class Control(Enum):
    PLAY = "play"
    PAUSE = "pause"

class ViewerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.caster = self.scope['url_route']['kwargs']['caster']
        await self.channel_layer.group_add(self.caster, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        self.channel_layer.group_discard(self.caster, self.channel_name)

    async def heartbeat(self, event):
        await self.send(text_data=json.dumps({
            'youtube_time': event['youtube_time']
        }))

    async def control(self, event):
        await self.send(text_data=json.dumps({
            'control': event['control']
        }))

class CasterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user = self.scope.get('user', None)
        if self.user.is_authenticated != True:
            await send_error('Not authenticated.', self.send)
            return await self.close()

    async def receive(self, text_data):
        if self.user == None:
            self.close()

        data = json.loads(text_data)
        url_path = data.get('url_path', None)
        if url_path == None:
            return await send_error('url_path must be a string.', self.send)

        time = data.get('time', None)
        if time == None:
            return await send_error('time must be a number.', self.send)

        query = Caster.objects.filter(user=self.user, url_path=url_path)
        if await sta(query.exists)() == False:
            return await send_error('No caster found.', self.send)

        caster = await sta(query.first)()
        caster.youtube_time = time
        await sta(caster.save)()
        await self.send(text_data=json.dumps({
            'status': 'ok'
        }))


async def send_error(message: str, send):
    return await send(text_data=json.dumps({
        'status': 'error',
        'message': message
    }))
