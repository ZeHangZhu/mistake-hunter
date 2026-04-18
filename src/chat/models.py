from django.db import models
from django.utils import timezone
from django.conf import settings


class Conversation(models.Model):
    """对话模型
    
    存储用户的AI对话会话
    """
    # 关联用户，级联删除
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name='用户',
        default=1
    )
    # 对话标题
    title = models.CharField(max_length=200, default='新对话')
    # 创建时间
    created_at = models.DateTimeField(default=timezone.now)
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 按更新时间倒序排列
        ordering = ['-updated_at']
        # 添加索引优化查询
        indexes = [
            models.Index(fields=['-updated_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        """返回对话标题作为字符串表示"""
        return self.title


class Message(models.Model):
    """消息模型
    
    存储对话中的每条消息
    """
    # 角色选择
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', '助手'),
    ]

    # 所属对话，级联删除
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    # 角色
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # 消息内容
    content = models.TextField()
    # 创建时间
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        # 按创建时间正序排列
        ordering = ['created_at']

    def __str__(self):
        """返回消息描述作为字符串表示"""
        return f'{self.role}: {self.content[:50]}'
