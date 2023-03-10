# import json

# from asgiref.sync import async_to_sync
# from channels.generic.websocket import WebsocketConsumer
# from .models import Message

# class ChatConsumer(WebsocketConsumer):
    
#     def fetch_messages(self,data):
#         print("fetch message")
#         messages=Message.last_10_message()
#         content={
#             "messages":self.messages_to_json(messages)
#         }
#         self.send_message(content)
         

#     def new_message(self,data):
#         print("new message")
#         pass 

#     def messages_to_json(self,messages):
#         result=[]
#         for message in messages:
#             result.append(self.message_to_json(message))
#         return result
    
#     def message_to_json(self,message):
#         return {
#             'author':message.author,
#             'conent':message.content,
#             'timestamp':str(message.timestamp)
#         }
#     commands={
#         "fetch_messages":fetch_messages,
#         "new_message":new_message
#     }

#     def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = "chat_%s" % self.room_name

#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, self.channel_name
#         )

#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name, self.channel_name
#         )

#     # Receive message from WebSocket
#     def receive(self, text_data):
#         data = json.loads(text_data)
#         # message = data["message"]
#         self.commands[data['command']](self,data)

#     def send_chat_message(self,message):
#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name, {"type": "chat_message", "message": message}
#         )

#     # Receive message from room group

#     def send_message(self,message):
#         self.send(text_data=json.dumps(message)) 

#     def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({"message": message}))



from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Message
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def save_message(self, author, content):
        message = Message(author=author, content=content)
        message.save()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        author = self.scope['user']
        await self.save_message(author, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'author': author.username,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        author = event['author']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'author': author,
        }))
