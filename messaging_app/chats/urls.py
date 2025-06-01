from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import ConversationViewSet, MessageViewSet

# Initialize the default router for REST framework
default_router = DefaultRouter()

# Register the conversation viewset with the default router
# This creates standard REST endpoints for conversations
default_router.register(
    r'conversations',
    ConversationViewSet,
    basename='conversation'
)

# Create a nested router for messages within conversations
# This creates nested REST endpoints for messages
conversations_router = routers.NestedDefaultRouter(
    default_router,
    r'conversations',
    lookup='conversation'
)
conversations_router.register(
    r'messages',
    MessageViewSet,
    basename='conversation-messages'
)

# Combine all router URLs
urlpatterns = [
    # Include the default router URLs
    path('', include(default_router.urls)),
    # Include the nested router URLs
    path('', include(conversations_router.urls)),
]

# Explicitly use DefaultRouter for documentation
routers.DefaultRouter() 