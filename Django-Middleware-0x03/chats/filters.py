import django_filters
from django_filters import rest_framework as filters
from .models import Message, Conversation
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class MessageFilter(filters.FilterSet):
    """
    Filter class for Message model that allows filtering by:
    - Time range (created_after, created_before)
    - Read status (is_read)
    - Sender (sender)
    - Content (content)
    """
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter messages created after this datetime (format: YYYY-MM-DD HH:MM:SS)'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter messages created before this datetime (format: YYYY-MM-DD HH:MM:SS)'
    )
    sender = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        help_text='Filter messages by sender'
    )
    is_read = filters.BooleanFilter(
        help_text='Filter messages by read status'
    )
    conversation = filters.ModelChoiceFilter(
        queryset=Conversation.objects.all(),
        help_text='Filter messages by conversation'
    )
    content = filters.CharFilter(
        lookup_expr='icontains',
        help_text='Filter messages by content (case-insensitive)'
    )

    class Meta:
        model = Message
        fields = ['sender', 'is_read', 'conversation', 'created_after', 'created_before', 'content']

class ConversationFilter(filters.FilterSet):
    """
    Filter class for Conversation model that allows filtering by:
    - Participant (participant)
    - Name (name)
    """
    participants = filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        field_name='participants',
        lookup_expr='in',
        help_text='Filter conversations by participants'
    )
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter conversations created after this datetime (format: YYYY-MM-DD HH:MM:SS)'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter conversations created before this datetime (format: YYYY-MM-DD HH:MM:SS)'
    )
    name = filters.CharFilter(
        lookup_expr='icontains',
        help_text='Filter conversations by name (case-insensitive)'
    )
    last_message_after = filters.DateTimeFilter(
        field_name='messages__created_at',
        lookup_expr='gte',
        help_text='Filter conversations with messages after this datetime'
    )

    class Meta:
        model = Conversation
        fields = ['participants', 'name', 'created_after', 'created_before', 'last_message_after'] 