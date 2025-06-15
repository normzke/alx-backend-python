from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.vary import vary_on_cookie
from .models import Message, Notification

@login_required
@cache_page(60)  # Cache for 60 seconds
@vary_on_cookie  # Vary cache by user
def conversation_list(request):
    """View to display all conversations for the current user"""
    threads = Message.get_user_threads(request.user)
    
    return render(request, 'messaging/conversation_list.html', {
        'threads': threads
    })

@login_required
@cache_page(60)  # Cache for 60 seconds
@vary_on_cookie  # Vary cache by user
def thread_detail(request, thread_id):
    """View to display a specific thread with all its replies"""
    thread_messages = Message.get_thread(thread_id)
    
    if not thread_messages.exists():
        messages.error(request, 'Thread not found.')
        return redirect('conversation_list')
    
    # Mark messages as read
    thread_messages.filter(receiver=request.user, read=False).update(read=True)
    
    return render(request, 'messaging/thread_detail.html', {
        'messages': thread_messages,
        'root_message': thread_messages.first()
    })

@login_required
@cache_page(60)  # Cache for 60 seconds
@vary_on_cookie  # Vary cache by user
def inbox(request):
    """View to display unread messages in user's inbox"""
    unread_messages = Message.unread.for_user(request.user)
    unread_count = Message.unread.get_unread_count(request.user)
    
    return render(request, 'messaging/inbox.html', {
        'unread_messages': unread_messages,
        'unread_count': unread_count
    })

@login_required
def mark_messages_read(request):
    """View to mark messages as read"""
    if request.method == 'POST':
        message_ids = request.POST.getlist('message_ids[]')
        if message_ids:
            Message.unread.mark_as_read(request.user, message_ids)
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def reply_to_message(request, message_id):
    """View to handle replies to messages"""
    parent_message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            reply = Message.objects.create(
                sender=request.user,
                receiver=parent_message.sender if request.user == parent_message.receiver else parent_message.receiver,
                content=content,
                parent_message=parent_message
            )
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': reply.id,
                    'content': reply.content,
                    'sender': reply.sender.username,
                    'timestamp': reply.timestamp.isoformat()
                }
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def delete_user(request):
    """View to handle user account deletion"""
    if request.method == 'POST':
        # Verify password before deletion
        password = request.POST.get('password')
        if not request.user.check_password(password):
            messages.error(request, 'Incorrect password. Please try again.')
            return render(request, 'messaging/delete_account.html')
        
        try:
            with transaction.atomic():
                # Delete the user (this will trigger the post_delete signal)
                user = request.user
                logout(request)  # Log out the user before deletion
                user.delete()
                messages.success(request, 'Your account has been successfully deleted.')
                return redirect('login')
        except Exception as e:
            messages.error(request, f'An error occurred while deleting your account: {str(e)}')
            return render(request, 'messaging/delete_account.html')
    
    return render(request, 'messaging/delete_account.html')

@login_required
def notifications(request):
    """View to display user's notifications"""
    notifications = Notification.objects.filter(
        user=request.user
    ).select_related('message', 'message__sender').order_by('-created_at')
    
    return render(request, 'messaging/notifications.html', {
        'notifications': notifications
    }) 