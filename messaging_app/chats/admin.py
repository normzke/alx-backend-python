from django.contrib import admin
from .models import Conversation, Message, MessageHistory, Notification

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    filter_horizontal = ('participants',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'conversation', 'timestamp', 'edited', 'read')
    list_filter = ('edited', 'read', 'timestamp')
    search_fields = ('content', 'sender__username')

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'edited_at')
    list_filter = ('edited_at',)
    search_fields = ('content', 'message__sender__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('user__username', 'message__content')
