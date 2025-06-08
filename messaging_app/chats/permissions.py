from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    This permission class handles both conversation and message access.
    """
    def has_permission(self, request, view):
        # Ensure user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant of the conversation
        if hasattr(obj, 'conversation'):
            # For Message objects
            return request.user in obj.conversation.participants.all()
        elif hasattr(obj, 'participants'):
            # For Conversation objects
            return request.user in obj.participants.all()
        return False

class IsMessageSender(permissions.BasePermission):
    """
    Custom permission to only allow message sender to update or delete their messages.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any participant
        if request.method in permissions.SAFE_METHODS:
            return IsParticipantOfConversation().has_object_permission(request, view, obj)
        
        # Write permissions are only allowed to the sender of the message
        return obj.sender == request.user 