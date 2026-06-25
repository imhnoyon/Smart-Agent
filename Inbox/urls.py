from django.urls import path
from .views import *

urlpatterns = [
    path('conversations/', ConversationList.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/messages/', MessageListCreate.as_view(), name='message-list-create'),
    path('conversations/<int:pk>/suggest-reply/', SuggestReply.as_view(), name='suggest-reply'),
    path('conversations/<int:pk>/lock/', LockDetail.as_view(), name='lock-detail'),
    path('conversations/<int:pk>/lock/acquire/', LockAcquire.as_view(), name='lock-acquire'),
    path('conversations/<int:pk>/lock/release/', LockRelease.as_view(), name='lock-release'),
]
