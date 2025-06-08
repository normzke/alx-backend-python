from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        return request.user in obj.participants.all()

class IsMessageSender(permissions.BasePermission):
    """
    Custom permission to only allow message sender to modify or delete their messages.
    """
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS requests for all participants
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()
        
        # Allow PUT, PATCH, DELETE only for message sender
        return obj.sender == request.user 