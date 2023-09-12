import json
import os

import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from chat.models import  RoomMessage
from channels.db import database_sync_to_async

import logging

logger = logging.getLogger(__name__)

dt = serializers.DateTimeField()

redis_conn = redis.Redis(host=os.getenv('REDIS_HOST'), password=os.getenv('REDIS_PASSWORD'), db=0)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # Join room group
        user = self.scope['user']
        if not user.is_authenticated:
                return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        chat = RoomMessage(
                chat_room_id=self.room_id,
                message=text_data_json['message'],
                sent_by = self.scope['user'],
            )
            
        await database_sync_to_async(chat.save)()

        await self.channel_layer.group_send(
                self.room_group_name,{
                'type': 'chat_message',
                'message': message,
                'created_at': str(timezone.now()),
            }
        )
    
    async def chat_message(self, event):
        """
        This method sends a WebSocket message to the connected client.
        """
        await self.send(text_data=json.dumps(
            {
            "message": event['message'],
            "created_at": event['created_at']}))