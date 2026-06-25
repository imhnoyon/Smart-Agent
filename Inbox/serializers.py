from rest_framework import serializers
from .models import Conversation, Message
from .lock_manager import get_lock_state
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that accepts `email` + `password`
    instead of the default `username` + `password`.
    """
    username_field = get_user_model().EMAIL_FIELD  # 'email'

    def validate(self, attrs):
        User = get_user_model()
        email = attrs.get('email') or attrs.get(self.username_field)
        password = attrs.get('password')

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'detail': 'No account found with this email address.'}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {'detail': 'Incorrect password.'}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {'detail': 'This account is inactive.'}
            )

        # Generate tokens directly — avoids Django's authenticate() which
        # requires the username field, not email.
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'customer_name', 'last_message', 'status', 'sentiment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'sentiment', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        return last_msg.message if last_msg else None


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'message', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user:
            return attrs

        # Get conversation_id from the view's URL kwargs
        view = self.context.get('view')
        if not view:
            return attrs
            
        conversation_id = view.kwargs.get('pk') or view.kwargs.get('conversation_id')
        if not conversation_id:
            return attrs

        # Verify concurrency lock state
        lock_state = get_lock_state(conversation_id)
        if lock_state['locked'] and lock_state['owner_id'] != request.user.id:
            raise serializers.ValidationError(
                {"detail": f"This conversation is locked by agent '{lock_state['owner_username']}'."}
            )

        return attrs
