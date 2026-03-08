from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
    )
    email = models.EmailField(unique=True, verbose_name='邮箱')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student', verbose_name='用户类型')
    is_active = models.BooleanField(default=False, verbose_name='是否激活')
    daily_review_limit = models.IntegerField(default=10, verbose_name='每日复习题目数量')
    points = models.IntegerField(default=0, verbose_name='积分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username


class Class(models.Model):
    name = models.CharField(max_length=100, verbose_name='班级名称')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_classes', verbose_name='创建教师')
    students = models.ManyToManyField(User, related_name='classes', verbose_name='学生列表')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'classes'
        verbose_name = '班级'
        verbose_name_plural = '班级'

    def __str__(self):
        return self.name
