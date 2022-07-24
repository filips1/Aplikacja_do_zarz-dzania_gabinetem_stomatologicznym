import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from chat.models import Thread, ChatMessage

class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })
        other_user = self.scope['url_route']['kwargs']['username']
        me = self.scope['user']
        thread_obj = await self.get_thread(me, other_user)
        print(other_user,me)
        print(thread_obj)
        self.thread_obj = thread_obj
        chat_room = f"thread_{thread_obj.id}"
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
    async def websocket_receive(self, event):
        print("receive", event)
        front_text = event.get('text', None)
        if front_text is not None:
            loaded_dict_data = json.loads(front_text)
            msg = loaded_dict_data.get('message')
            print(msg)
            user = self.scope['user']
            myResponse = {
                'message': msg,
                'username': user.username
            }
            await self.create_new_message(msg)

            await self.channel_layer.group_send(
                self.chat_room,
                {
                    "type": "chat_mes",
                    "text": json.dumps(myResponse)
                }
                )

    async def chat_mes(self, event):
        print('message', event)
        await self.send({
            "type": "websocket.send",
            "text": event['text']
            })

    async def websocket_disconnect(self, event):
        print("disconnect", event)

    @database_sync_to_async
    def get_thread(self,user,other_username):
        return Thread.objects.get_or_new(user,other_username)[0]

    @database_sync_to_async
    def create_new_message(self,message):
        thread_obj = self.thread_obj
        user = self.scope['user']
        return ChatMessage.objects.create(thread = thread_obj, user = user, message = message)
