from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsMessageSender
from .filters import MessageFilter, ConversationFilter
from django.contrib.auth.models import User

# Create your views here.

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__username', 'name']
    ordering_fields = ['created_at', 'name']
    filterset_class = ConversationFilter

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        try:
            conversation = serializer.save()
            conversation.participants.add(self.request.user)
            return conversation
        except Exception as e:
            raise ValidationError(f"Error creating conversation: {str(e)}")

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        try:
            conversation = self.get_object()
            user_id = request.data.get('user_id')
            
            if not user_id:
                raise ValidationError("user_id is required")
                
            if not User.objects.filter(id=user_id).exists():
                raise ValidationError("User does not exist")
                
            conversation.participants.add(user_id)
            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f"Error adding participant: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation, IsMessageSender]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content']
    ordering_fields = ['created_at', 'is_read']
    filterset_class = MessageFilter

    def get_queryset(self):
        try:
            conversation_id = self.kwargs.get('conversation_pk')
            if conversation_id:
                return Message.objects.filter(
                    conversation_id=conversation_id,
                    conversation__participants=self.request.user
                )
            return Message.objects.none()
        except Exception as e:
            raise ValidationError(f"Error retrieving messages: {str(e)}")

    def perform_create(self, serializer):
        try:
            conversation_id = self.kwargs.get('conversation_pk')
            conversation = get_object_or_404(
                Conversation.objects.filter(participants=self.request.user),
                id=conversation_id
            )
            serializer.save(sender=self.request.user, conversation=conversation)
        except Exception as e:
            raise ValidationError(f"Error creating message: {str(e)}")

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
