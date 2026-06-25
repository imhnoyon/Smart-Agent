from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken


@database_sync_to_async
def get_user_from_token(token_string):
    """
    Validate JWT token and return user object
    """
    try:
        token = AccessToken(token_string)
        user_id = token['user_id']
        User = get_user_model()
        return User.objects.get(id=int(user_id))
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    Middleware to authenticate WebSocket connections using JWT token from query string.
    Usage: ws://localhost:8001/ws/conversations/1/?token=YOUR_JWT_TOKEN
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode()
        token = None
        
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                if key == 'token':
                    token = value
                    break

        # Authenticate user
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)
