from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='邮箱')
    is_active = models.BooleanField(default=False, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username
