import django_filters
from django_filters import rest_framework as filters
from .models import Message, Conversation
from django.contrib.auth.models import User

class MessageFilter(filters.FilterSet):
    """
    Filter class for Message model that allows filtering by:
    - Time range (created_after, created_before)
    - Read status (is_read)
    - Sender (sender)
    - Content (content)
    """
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    sender = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_read = filters.BooleanFilter()
    conversation = filters.ModelChoiceFilter(queryset=Conversation.objects.all())

    class Meta:
        model = Message
        fields = ['sender', 'is_read', 'conversation', 'created_after', 'created_before']

class ConversationFilter(filters.FilterSet):
    """
    Filter class for Conversation model that allows filtering by:
    - Participant (participant)
    - Name (name)
    """
    participants = filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        field_name='participants',
        lookup_expr='in'
    )
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Conversation
        fields = ['participants', 'name', 'created_after', 'created_before'] 