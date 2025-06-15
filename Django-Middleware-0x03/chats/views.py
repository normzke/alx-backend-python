from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsAuthenticatedUser, IsParticipantOfConversation, IsMessageSender
from .filters import MessageFilter, ConversationFilter
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse

# Create your views here.

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticatedUser, IsParticipantOfConversation]
    pagination_class = PageNumberPagination
    filterset_class = ConversationFilter
    search_fields = ['name', 'participants__username']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        conversation.participants.add(user_id)
        return Response(
            {'status': 'participant added'}, 
            status=status.HTTP_200_OK
        )

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedUser, IsMessageSender]
    pagination_class = PageNumberPagination
    filterset_class = MessageFilter
    search_fields = ['content']
    ordering_fields = ['created_at', 'is_read']

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_pk')
        if conversation_id:
            return Message.objects.filter(conversation_id=conversation_id)
        return Message.objects.none()

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_pk')
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        if self.request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not a participant in this conversation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer.save(sender=self.request.user, conversation=conversation)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {'error': 'You can only update your own messages'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {'error': 'You can only delete your own messages'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, conversation_pk=None, pk=None):
        try:
            message = self.get_object()
            message.is_read = True
            message.save()
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f"Error marking message as read: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def index(request):
    return HttpResponse("Welcome to the Chat App!")
