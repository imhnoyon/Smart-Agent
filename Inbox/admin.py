from django.contrib import admin
from .models import *


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'created_at')
    search_fields = ('customer_name',)
    list_filter = ('status', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'message', 'timestamp')
    search_fields = ('message',)
    list_filter = ('timestamp',)
