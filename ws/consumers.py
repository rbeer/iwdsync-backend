from asgiref.sync import sync_to_async as sta
from channels.auth import get_user
from channels.generic.websocket import AsyncWebsocketConsumer
from enum import Enum
import json
import re

from caster.models import Caster
from iwdsync.log import logger

class MESSAGE_TYPE(Enum):
    HEARTBEAT = 0
    CONTROL = 1

class CONTROL_ACTION(Enum):
    PLAY = 1
    PAUSE = 2
    SET_VIDEO = 3

class ViewerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.caster = self.scope['url_route']['kwargs']['caster']
        logger.debug('[%s] Adding viewer to group', self.caster)
        await self.channel_layer.group_add(self.caster, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        logger.debug('[%s] Removing viewer from group', self.caster)
        await self.channel_layer.group_discard(self.caster, self.channel_name)

    async def heartbeat(self, event):
        await self.send(text_data=json.dumps({
            'type': MESSAGE_TYPE.HEARTBEAT.name,
            'youtube_time': event['youtube_time']
        }))

    async def control(self, event):
        message = {
            'type': MESSAGE_TYPE.CONTROL.name,
            'action': event['action']
        }
        if event['action'] == CONTROL_ACTION.SET_VIDEO.name:
            message['videoId'] = event['videoId']

        await self.send(text_data=json.dumps(message))

class CasterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user = self.scope.get('user', None)
        self.url_path = self.scope['url_route']['kwargs']['caster']

        if self.user == None or self.user.is_authenticated != True:
            self.log_error('Rejecting unauthenticated caster connection')
            await send_error('Not authenticated.', self.send)
            return await self.close()

        query = Caster.objects.filter(user=self.user, url_path=self.url_path)
        if await sta(query.exists)() == False:
            self.log_error('Authenticated user has no caster')
            return await send_error('No caster found.', self.send)

        self.caster = await sta(query.first)()

        logger.info('[%s] caster connected', self.url_path)

    async def receive(self, text_data):
        if self.user == None:
            await self.close()

        data = json.loads(text_data)
        message_type = data.get('type', None)
        if message_type not in MESSAGE_TYPE._member_names_:
            return await send_error(f"type must be one of {MESSAGE_TYPE._member_names_}", self.send)

        if message_type == MESSAGE_TYPE.HEARTBEAT.name:
            return await self.handle_heartbeat_message(data)
        if message_type == MESSAGE_TYPE.CONTROL.name:
            return await self.handle_control_message(data)

    async def handle_heartbeat_message(self, data: dict):
        if self.url_path == None:
            return await send_error('url_path must be a string.', self.send)

        time = data.get('youtube_time', None)
        if time == None:
            return await send_error('youtube_time must be a number.', self.send)

        logger.info('[%s] Updating youtube_time', self.url_path)
        self.caster.youtube_time = time
        await sta(self.caster.save)()

        logger.info('[%s] Relaying to youtube_time', self.url_path)
        await self.channel_layer.group_send(self.url_path, {
            'type': 'heartbeat',
            'youtube_time': time
        })

        await self.send(text_data=json.dumps({
            'status': 'ok'
        }))

    async def handle_control_message(self, data: dict):
        action = data.get('action', None)
        if action not in CONTROL_ACTION._member_names_:
            return await send_error(f"action must be one of {CONTROL_ACTION._member_names_}", self.send)

        message = {
            'type': 'control',
            'action': action
        }

        if action == CONTROL_ACTION.SET_VIDEO.name:
            video_id = data.get('videoId', '')
            id_format_match = re.fullmatch('[a-zA-Z0-9_-]{11}', video_id)

            if id_format_match is None:
                return await send_error('videoId must be a valid Youtube video id', self.send)

            message['videoId'] = video_id
            logger.info('[%s] %sing video to %s', self.url_path, action, video_id)
        else:
            logger.info('[%s] %sing video', self.url_path, action)

        print(message)
        await self.channel_layer.group_send(self.url_path, message)

    def log_error(self, message: str):
        logger.error('[%s] %s', self.url_path, message)

async def send_error(message: str, send):
    return await send(text_data=json.dumps({
        'status': 'error',
        'message': message
    }))
