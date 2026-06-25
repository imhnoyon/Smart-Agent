
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.pagination import PageNumberPagination
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .lock_manager import get_lock_state, acquire_lock, release_lock
from .services.suggestion_engine import get_suggestion
from .tasks import  conversation_sentiment


class ConversationList(APIView):
    def get(self, request):
        queryset = Conversation.objects.all().order_by('-created_at')
        status_param = request.query_params.get('status')
        search_param = request.query_params.get('search')

        if status_param:
            queryset = queryset.filter(status=status_param)
        if search_param:
            queryset = queryset.filter(customer_name__icontains=search_param)

        # Pagination using DRF PageNumberPagination
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = ConversationSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ConversationSerializer(queryset, many=True)
        return Response(serializer.data)


class MessageListCreate(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        messages = conversation.messages.all().order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        serializer = MessageSerializer(
            data=request.data,
            context={'request': request, 'view': self}
        )
        serializer.is_valid(raise_exception=True)
        message_obj = serializer.save(conversation=conversation)
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"conversation_{pk}",
                {
                    "type": "broadcast_event",
                    "payload": {
                        "event": "message_created",
                        "message": MessageSerializer(message_obj).data
                    }
                }
            )

        if message_obj.sender == 'agent':
            conversation_sentiment.delay(conversation.id)

        return Response(MessageSerializer(message_obj).data, status=status.HTTP_201_CREATED)


class SuggestReply(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        get_object_or_404(Conversation, pk=pk)
        message_text = request.data.get('message', '')
        suggestion = get_suggestion(message_text)
        return Response({"suggestion": suggestion}, status=status.HTTP_200_OK)


class LockDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        get_object_or_404(Conversation, pk=pk)
        lock_state = get_lock_state(pk)
        return Response(lock_state, status=status.HTTP_200_OK)


class LockAcquire(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        get_object_or_404(Conversation, pk=pk)
        success, lock_state = acquire_lock(pk, request.user)
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"conversation_{pk}",
                {
                    "type": "broadcast_event",
                    "payload": {
                        "event": "lock_status_changed",
                        "lock_state": lock_state
                    }
                }
            )
        if success:
            return Response(
                {"message": "Lock acquired successfully", "lock_state": lock_state},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "detail": f"This conversation is locked by agent '{lock_state['owner_email']}'.",
                    "lock_state": lock_state
                },
                status=status.HTTP_409_CONFLICT
            )


class LockRelease(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        get_object_or_404(Conversation, pk=pk)
        success, msg = release_lock(pk, request.user)
        lock_state = get_lock_state(pk)
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"conversation_{pk}",
                {
                    "type": "broadcast_event",
                    "payload": {
                        "event": "lock_status_changed",
                        "lock_state": lock_state
                    }
                }
            )

        if success:
            return Response({"message": msg}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": msg}, status=status.HTTP_403_FORBIDDEN)
