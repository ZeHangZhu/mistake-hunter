from django.db import models
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name='学科名称')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subjects',
        verbose_name='用户'
    )
    color = models.CharField(max_length=7, default='#007bff', verbose_name='主题颜色')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'subjects'
        verbose_name = '学科'
        verbose_name_plural = '学科'
        unique_together = ['user', 'name']
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name='分组名称')
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name='所属学科'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父分组'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mistake_groups',
        verbose_name='用户'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'groups'
        verbose_name = '分组'
        verbose_name_plural = '分组'

    def __str__(self):
        return self.name


class KnowledgePoint(models.Model):
    name = models.CharField(max_length=100, verbose_name='知识点名称')
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='knowledge_points',
        verbose_name='所属学科'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='knowledge_points',
        verbose_name='用户'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'knowledge_points'
        verbose_name = '知识点'
        verbose_name_plural = '知识点'
        unique_together = ['user', 'subject', 'name']

    def __str__(self):
        return self.name


class Mistake(models.Model):
    MASTERY_LEVEL_CHOICES = [
        ('to_review', '待复习'),
        ('mastered', '已掌握'),
    ]

    DIFFICULTY_CHOICES = [
        (1, '简单'),
        (2, '中等'),
        (3, '困难'),
    ]

    ERROR_CAUSE_CHOICES = [
        ('knowledge', '知识性错误'),
        ('logic', '逻辑性错误'),
        ('habit', '习惯性错误'),
        ('custom', '自定义'),
    ]

    title = models.CharField(max_length=200, verbose_name='题目标题')
    content = models.TextField(verbose_name='题干内容')
    solution = models.TextField(blank=True, verbose_name='解题过程')
    correct_answer = models.TextField(blank=True, verbose_name='正确答案')
    user_answer = models.TextField(blank=True, verbose_name='用户答案')
    analysis = models.TextField(blank=True, verbose_name='错因分析')
    error_cause = models.CharField(
        max_length=20,
        choices=ERROR_CAUSE_CHOICES,
        default='knowledge',
        verbose_name='错因类型'
    )
    custom_error_cause = models.CharField(max_length=100, blank=True, verbose_name='自定义错因')
    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        default=2,
        verbose_name='难度'
    )
    mastery_level = models.CharField(
        max_length=20,
        choices=MASTERY_LEVEL_CHOICES,
        default='to_review',
        verbose_name='掌握程度'
    )
    review_count = models.IntegerField(default=0, verbose_name='复习次数')
    last_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='最后复习时间')
    next_review_at = models.DateTimeField(null=True, blank=True, verbose_name='下次复习时间')

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='mistakes',
        verbose_name='所属学科'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mistakes',
        verbose_name='所属分组'
    )
    knowledge_points = models.ManyToManyField(
        KnowledgePoint,
        blank=True,
        related_name='mistakes',
        verbose_name='知识点'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mistakes',
        verbose_name='用户'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'mistakes'
        verbose_name = '错题'
        verbose_name_plural = '错题'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class MistakeImage(models.Model):
    mistake = models.ForeignKey(
        Mistake,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='所属错题'
    )
    image = models.ImageField(upload_to='mistake_images/', verbose_name='图片')
    ocr_text = models.TextField(blank=True, verbose_name='OCR识别文字')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'mistake_images'
        verbose_name = '错题图片'
        verbose_name_plural = '错题图片'

    def __str__(self):
        return f'{self.mistake.title} - 图片'


class ReviewRecord(models.Model):
    RESULT_CHOICES = [
        ('mastered', '已掌握'),
        ('wrong_again', '再次错误'),
    ]

    mistake = models.ForeignKey(
        Mistake,
        on_delete=models.CASCADE,
        related_name='review_records',
        verbose_name='所属错题'
    )
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        verbose_name='复习结果'
    )
    notes = models.TextField(blank=True, verbose_name='复习笔记')
    reviewed_at = models.DateTimeField(auto_now_add=True, verbose_name='复习时间')

    class Meta:
        db_table = 'review_records'
        verbose_name = '复习记录'
        verbose_name_plural = '复习记录'
        ordering = ['-reviewed_at']

    def __str__(self):
        return f'{self.mistake.title} - {self.get_result_display()}'


class ReviewImage(models.Model):
    review_record = models.ForeignKey(
        ReviewRecord,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='所属复习记录'
    )
    image = models.ImageField(upload_to='review_images/', verbose_name='图片')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'review_images'
        verbose_name = '复习图片'
        verbose_name_plural = '复习图片'

    def __str__(self):
        return f'{self.review_record} - 图片'
