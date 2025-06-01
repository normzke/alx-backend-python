from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'bio', 'profile_picture', 'created_at']
        read_only_fields = ['created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'sender_name', 'message_body', 'sent_at', 'is_read']
        read_only_fields = ['sent_at', 'is_read']

    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'last_message', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['created_at', 'updated_at']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def validate_participants(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants")
        return value 