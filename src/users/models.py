from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """用户模型，继承自Django的AbstractUser
    
    扩展了默认用户模型，添加了用户类型、积分等字段，
    支持学生和教师两种用户角色
    """
    # 用户类型选择
    USER_TYPE_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
    )
    
    # 邮箱字段，唯一
    email = models.EmailField(unique=True, verbose_name='邮箱')
    # 用户类型，默认为学生
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student', verbose_name='用户类型')
    # 是否激活
    is_active = models.BooleanField(default=False, verbose_name='是否激活')
    # 每日复习题目数量限制
    daily_review_limit = models.IntegerField(default=10, verbose_name='每日复习题目数量')
    # 用户积分
    points = models.IntegerField(default=0, verbose_name='积分')
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        """返回用户的用户名作为字符串表示"""
        return self.username


class Class(models.Model):
    """班级模型
    
    用于教师创建班级并管理学生
    """
    # 班级名称
    name = models.CharField(max_length=100, verbose_name='班级名称')
    # 创建教师，级联删除
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_classes', verbose_name='创建教师')
    # 学生列表，多对多关系
    students = models.ManyToManyField(User, related_name='classes', verbose_name='学生列表')
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'classes'
        verbose_name = '班级'
        verbose_name_plural = '班级'

    def __str__(self):
        """返回班级名称作为字符串表示"""
        return self.name
