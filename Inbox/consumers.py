import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from .models import Conversation, Message


class ConversationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time conversation updates.
    Handles both agent and customer messages.
    """

    async def connect(self):
        """Accept WebSocket connection and join conversation group"""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f"conversation_{self.conversation_id}"
        
        # Check if user is authenticated (JWT middleware sets this)
        user = self.scope.get('user')
        if not user or user.is_anonymous:
            await self.close(code=4001)
            return

        # Join conversation group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Leave conversation group on disconnect"""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        Expected format: {"sender": "agent", "message": "Hello"}
        """
        try:
            data = json.loads(text_data)
            sender = data.get('sender')
            message_text = data.get('message')

            # Validate input
            if not sender or sender not in ['agent', 'customer']:
                await self.send(text_data=json.dumps({
                    'error': 'sender must be "agent" or "customer"'
                }))
                return

            if not message_text:
                await self.send(text_data=json.dumps({
                    'error': 'message is required'
                }))
                return

            # Save message to database
            message_obj = await self.save_message(sender, message_text)

            # Broadcast to all connected clients in this conversation
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'broadcast_message',
                    'message': {
                        'id': message_obj.id,
                        'sender': message_obj.sender,
                        'message': message_obj.message,
                        'timestamp': message_obj.timestamp.isoformat()
                    }
                }
            )

            # Trigger sentiment analysis for agent messages
            if sender == 'agent':
                await self.trigger_sentiment_analysis()

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Server error: {str(e)}'
            }))

    async def broadcast_message(self, event):
        """
        Receive message from group broadcast and send to WebSocket
        """
        await self.send(text_data=json.dumps({
            'event': 'message_created',
            'message': event['message']
        }))

    async def broadcast_event(self, event):
        """
        Generic event broadcaster for lock updates, etc.
        """
        await self.send(text_data=json.dumps(event['payload']))

    @database_sync_to_async
    def save_message(self, sender, message_text):
        """Save message to database"""
        conversation = get_object_or_404(Conversation, pk=self.conversation_id)
        return Message.objects.create(
            conversation=conversation,
            sender=sender,
            message=message_text
        )

    @database_sync_to_async
    def trigger_sentiment_analysis(self):
        """Trigger Celery task for sentiment analysis"""
        from .tasks import analyze_conversation_sentiment_task
        analyze_conversation_sentiment_task.delay(int(self.conversation_id))
