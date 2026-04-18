from django.db import models
from django.conf import settings


class SocraticSession(models.Model):
    """苏格拉底对话会话模型
    
    用于AI辅导功能，通过问答方式帮助学生理解错题
    """
    # 所属错题，级联删除
    mistake = models.ForeignKey(
        'mistakes.Mistake',
        on_delete=models.CASCADE,
        related_name='socratic_sessions',
        verbose_name='所属错题'
    )
    # 关联用户，级联删除
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='socratic_sessions',
        verbose_name='用户'
    )
    # 开始时间
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    # 结束时间，可空
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    # 是否进行中
    is_active = models.BooleanField(default=True, verbose_name='是否进行中')

    class Meta:
        db_table = 'socratic_sessions'
        verbose_name = '苏格拉底对话'
        verbose_name_plural = '苏格拉底对话'
        ordering = ['-started_at']

    def __str__(self):
        """返回会话描述作为字符串表示"""
        return f'{self.user.username} - {self.mistake.title}'


class SocraticMessage(models.Model):
    """苏格拉底对话消息模型
    
    存储对话中的每条消息，包括用户和AI的消息
    """
    # 角色选择
    ROLE_CHOICES = [
        ('user', '用户'),
        ('ai', 'AI'),
    ]

    # 所属会话，级联删除
    session = models.ForeignKey(
        SocraticSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='所属会话'
    )
    # 角色
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='角色'
    )
    # 消息内容
    content = models.TextField(verbose_name='消息内容')
    # 是否是卡点
    is_stuck_point = models.BooleanField(default=False, verbose_name='是否是卡点')
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'socratic_messages'
        verbose_name = '苏格拉底消息'
        verbose_name_plural = '苏格拉底消息'
        ordering = ['created_at']

    def __str__(self):
        """返回消息描述作为字符串表示"""
        return f'{self.get_role_display()}: {self.content[:30]}...'




class ReviewPlan(models.Model):
    """复习计划模型
    
    用于管理学生的错题复习计划
    """
    # 关联用户，级联删除
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_plans',
        verbose_name='用户'
    )
    # 关联错题，级联删除
    mistake = models.ForeignKey(
        'mistakes.Mistake',
        on_delete=models.CASCADE,
        related_name='review_plans',
        verbose_name='错题'
    )
    # 计划复习日期
    scheduled_date = models.DateField(verbose_name='计划复习日期')
    # 是否已完成
    is_completed = models.BooleanField(default=False, verbose_name='是否已完成')
    # 完成时间，可空
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'review_plans'
        verbose_name = '复习计划'
        verbose_name_plural = '复习计划'
        ordering = ['scheduled_date']

    def __str__(self):
        """返回复习计划描述作为字符串表示"""
        return f'{self.user.username} - {self.mistake.title} - {self.scheduled_date}'
