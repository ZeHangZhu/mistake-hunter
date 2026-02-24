from django.db import models
from django.conf import settings


class SocraticSession(models.Model):
    mistake = models.ForeignKey(
        'mistakes.Mistake',
        on_delete=models.CASCADE,
        related_name='socratic_sessions',
        verbose_name='所属错题'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='socratic_sessions',
        verbose_name='用户'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    is_active = models.BooleanField(default=True, verbose_name='是否进行中')

    class Meta:
        db_table = 'socratic_sessions'
        verbose_name = '苏格拉底对话'
        verbose_name_plural = '苏格拉底对话'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user.username} - {self.mistake.title}'


class SocraticMessage(models.Model):
    ROLE_CHOICES = [
        ('user', '用户'),
        ('ai', 'AI'),
    ]

    session = models.ForeignKey(
        SocraticSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='所属会话'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='角色'
    )
    content = models.TextField(verbose_name='消息内容')
    is_stuck_point = models.BooleanField(default=False, verbose_name='是否是卡点')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'socratic_messages'
        verbose_name = '苏格拉底消息'
        verbose_name_plural = '苏格拉底消息'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.get_role_display()}: {self.content[:30]}...'


class SimilarProblem(models.Model):
    original_mistake = models.ForeignKey(
        'mistakes.Mistake',
        on_delete=models.CASCADE,
        related_name='similar_problems',
        verbose_name='原错题'
    )
    title = models.CharField(max_length=200, verbose_name='题目标题')
    content = models.TextField(verbose_name='题干内容')
    solution = models.TextField(blank=True, verbose_name='解题过程')
    correct_answer = models.TextField(blank=True, verbose_name='正确答案')
    difficulty = models.IntegerField(
        choices=[(1, '简单'), (2, '中等'), (3, '困难')],
        default=2,
        verbose_name='难度'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='similar_problems',
        verbose_name='用户'
    )
    is_practiced = models.BooleanField(default=False, verbose_name='是否已练习')
    practiced_at = models.DateTimeField(null=True, blank=True, verbose_name='练习时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'similar_problems'
        verbose_name = '相似题'
        verbose_name_plural = '相似题'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ReviewPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_plans',
        verbose_name='用户'
    )
    mistake = models.ForeignKey(
        'mistakes.Mistake',
        on_delete=models.CASCADE,
        related_name='review_plans',
        verbose_name='错题'
    )
    scheduled_date = models.DateField(verbose_name='计划复习日期')
    is_completed = models.BooleanField(default=False, verbose_name='是否已完成')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'review_plans'
        verbose_name = '复习计划'
        verbose_name_plural = '复习计划'
        ordering = ['scheduled_date']

    def __str__(self):
        return f'{self.user.username} - {self.mistake.title} - {self.scheduled_date}'
