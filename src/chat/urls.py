from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='chat_index'),
    path('chat-stream/', views.chat_stream, name='chat_stream'),
    path('conversations/', views.get_conversations, name='get_conversations'),
    path('conversations/create/', views.create_conversation, name='create_conversation'),
    path('conversations/<int:conversation_id>/', views.get_conversation_messages, name='get_conversation_messages'),
    path('conversations/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('mistakes/', views.get_recent_mistakes, name='get_recent_mistakes'),
]
