from enum import Enum
import json
from asgiref.sync import sync_to_async as sta
from channels.auth import get_user
from channels.generic.websocket import AsyncWebsocketConsumer

from caster.models import Caster

class ViewerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.caster = self.scope['url_route']['kwargs']['caster']
        await self.channel_layer.group_add(self.caster, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.caster, self.channel_name)

    async def heartbeat(self, event):
        await self.send(text_data=json.dumps({
            'youtube_time': event['youtube_time']
        }))

    async def control(self, event):
        await self.send(text_data=json.dumps({
            'control': event['action']
        }))

class CasterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user = self.scope.get('user', None)
        self.url_path = self.scope['url_route']['kwargs']['caster']

        if self.user == None or self.user.is_authenticated != True:
            await send_error('Not authenticated.', self.send)
            return await self.close()

        query = Caster.objects.filter(user=self.user, url_path=self.url_path)
        if await sta(query.exists)() == False:
            return await send_error('No caster found.', self.send)

        self.caster = await sta(query.first)()


    async def receive(self, text_data):
        if self.user == None:
            await self.close()

        data = json.loads(text_data)
        print(self.scope)
        url_path = data.get('url_path', None)
        if url_path == None:
            return await send_error('url_path must be a string.', self.send)

        time = data.get('time', None)
        if time == None:
            return await send_error('time must be a number.', self.send)

        self.caster.youtube_time = time
        await sta(self.caster.save)()

        await self.channel_layer.group_send(self.caster.url_path, {
            'type': 'heartbeat',
            'youtube_time': time
        })

        await self.send(text_data=json.dumps({
            'status': 'ok'
        }))


async def send_error(message: str, send):
    return await send(text_data=json.dumps({
        'status': 'error',
        'message': message
    }))
