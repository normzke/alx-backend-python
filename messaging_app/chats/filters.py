import django_filters
from .models import Message
from django.utils import timezone
from datetime import timedelta

class MessageFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_read = django_filters.BooleanFilter(field_name='is_read')
    sender = django_filters.NumberFilter(field_name='sender__id')
    
    class Meta:
        model = Message
        fields = ['created_after', 'created_before', 'is_read', 'sender'] 