from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant of the conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return request.user in obj.participants.all() 