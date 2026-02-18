from django.db import models
from django.conf import settings


class AIChat(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_chats',
        verbose_name='用户'
    )
    title = models.CharField(max_length=200, verbose_name='对话标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ai_chats'
        verbose_name = 'AI对话'
        verbose_name_plural = 'AI对话'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', '助手'),
    ]

    chat = models.ForeignKey(
        AIChat,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='所属对话'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='角色'
    )
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'chat_messages'
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.get_role_display()}: {self.content[:50]}...'
