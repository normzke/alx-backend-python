import django_filters
from .models import Message, Conversation
from django.utils import timezone
from datetime import timedelta

class MessageFilter(django_filters.FilterSet):
    """
    Filter class for Message model that allows filtering by:
    - Time range (created_after, created_before)
    - Read status (is_read)
    - Sender (sender)
    - Content (content)
    """
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter messages created after this datetime'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter messages created before this datetime'
    )
    is_read = django_filters.BooleanFilter(
        field_name='is_read',
        help_text='Filter messages by read status'
    )
    sender = django_filters.NumberFilter(
        field_name='sender__id',
        help_text='Filter messages by sender ID'
    )
    content = django_filters.CharFilter(
        field_name='content',
        lookup_expr='icontains',
        help_text='Filter messages by content (case-insensitive)'
    )
    
    class Meta:
        model = Message
        fields = ['created_after', 'created_before', 'is_read', 'sender', 'content']

class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for Conversation model that allows filtering by:
    - Participant (participant)
    - Name (name)
    """
    participant = django_filters.NumberFilter(
        field_name='participants__id',
        help_text='Filter conversations by participant ID'
    )
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text='Filter conversations by name (case-insensitive)'
    )
    
    class Meta:
        model = Conversation
        fields = ['participant', 'name'] 