from django.db import models
from django.conf import settings


class Subject(models.Model):
    """学科模型
    
    用于用户创建和管理不同学科
    """
    # 学科名称
    name = models.CharField(max_length=100, verbose_name='学科名称')
    # 关联用户，级联删除
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subjects',
        verbose_name='用户'
    )
    # 主题颜色，默认为蓝色
    color = models.CharField(max_length=7, default='#007bff', verbose_name='主题颜色')
    # 排序值
    order = models.IntegerField(default=0, verbose_name='排序')
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'subjects'
        verbose_name = '学科'
        verbose_name_plural = '学科'
        # 每个用户的学科名称唯一
        unique_together = ['user', 'name']
        # 按排序和创建时间排序
        ordering = ['order', 'created_at']

    def __str__(self):
        """返回学科名称作为字符串表示"""
        return self.name


class Group(models.Model):
    """分组模型
    
    用于对同一学科下的错题进行分组管理，支持树形结构
    """
    # 分组名称
    name = models.CharField(max_length=100, verbose_name='分组名称')
    # 所属学科，级联删除
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name='所属学科'
    )
    # 父分组，支持树形结构
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父分组'
    )
    # 关联用户，级联删除
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mistake_groups',
        verbose_name='用户'
    )
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'groups'
        verbose_name = '分组'
        verbose_name_plural = '分组'

    def __str__(self):
        """返回分组名称作为字符串表示"""
        return self.name


class KnowledgePoint(models.Model):
    """知识点模型
    
    用于标记错题涉及的知识点
    """
    # 知识点名称
    name = models.CharField(max_length=100, verbose_name='知识点名称')
    # 所属学科，级联删除
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='knowledge_points',
        verbose_name='所属学科'
    )
    # 关联用户，级联删除
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='knowledge_points',
        verbose_name='用户'
    )
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'knowledge_points'
        verbose_name = '知识点'
        verbose_name_plural = '知识点'
        # 每个用户在同一学科下的知识点名称唯一
        unique_together = ['user', 'subject', 'name']

    def __str__(self):
        """返回知识点名称作为字符串表示"""
        return self.name


class Mistake(models.Model):
    """错题模型
    
    核心模型，存储用户的错题信息
    """
    # 掌握程度选择
    MASTERY_LEVEL_CHOICES = [
        ('to_review', '待复习'),
        ('mastered', '已掌握'),
    ]

    # 难度选择
    DIFFICULTY_CHOICES = [
        (1, '简单'),
        (2, '中等'),
        (3, '困难'),
    ]

    # 错因类型选择
    ERROR_CAUSE_CHOICES = [
        ('knowledge', '知识性错误'),
        ('logic', '逻辑性错误'),
        ('habit', '习惯性错误'),
        ('custom', '自定义'),
    ]

    # 题目标题
    title = models.CharField(max_length=200, blank=True, verbose_name='题目标题')
    # 题干内容
    content = models.TextField(verbose_name='题干内容')
    # 解题过程
    solution = models.TextField(blank=True, verbose_name='解题过程')
    # 正确答案
    correct_answer = models.TextField(blank=True, verbose_name='正确答案')
    # 用户答案
    user_answer = models.TextField(blank=True, verbose_name='用户答案')
    # 错因分析
    analysis = models.TextField(blank=True, verbose_name='错因分析')
    # 错因类型
    error_cause = models.CharField(
        max_length=20,
        choices=ERROR_CAUSE_CHOICES,
        default='knowledge',
        verbose_name='错因类型'
    )
    # 自定义错因
    custom_error_cause = models.CharField(max_length=100, blank=True, verbose_name='自定义错因')
    # 难度
    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        default=2,
        verbose_name='难度'
    )
    # 掌握程度
    mastery_level = models.CharField(
        max_length=20,
        choices=MASTERY_LEVEL_CHOICES,
        default='to_review',
        verbose_name='掌握程度'
    )
    # 复习次数
    review_count = models.IntegerField(default=0, verbose_name='复习次数')
    # 最后复习时间
    last_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='最后复习时间')
    # 下次复习时间
    next_review_at = models.DateTimeField(null=True, blank=True, verbose_name='下次复习时间')

    # 所属学科，级联删除
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='mistakes',
        verbose_name='所属学科'
    )
    # 所属分组，可空
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mistakes',
        verbose_name='所属分组'
    )
    # 关联知识点，多对多
    knowledge_points = models.ManyToManyField(
        KnowledgePoint,
        blank=True,
        related_name='mistakes',
        verbose_name='知识点'
    )
    # 关联用户，级联删除
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mistakes',
        verbose_name='用户'
    )

    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'mistakes'
        verbose_name = '错题'
        verbose_name_plural = '错题'
        # 按创建时间倒序排列
        ordering = ['-created_at']

    def __str__(self):
        """返回题目标题作为字符串表示"""
        return self.title


class MistakeImage(models.Model):
    """错题图片模型
    
    存储错题相关的图片，支持OCR识别
    """
    # 图片类型选择
    IMAGE_TYPE_CHOICES = [
        ('content', '题干图片'),
        ('solution', '解题过程图片'),
        ('correct_answer', '正确答案图片'),
        ('user_answer', '我的答案图片'),
    ]
    
    # 所属错题，级联删除
    mistake = models.ForeignKey(
        Mistake,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='所属错题'
    )
    # 图片文件
    image = models.ImageField(upload_to='mistake_images/', verbose_name='图片')
    # 图片类型
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPE_CHOICES,
        default='content',
        verbose_name='图片类型'
    )
    # OCR识别文字
    ocr_text = models.TextField(blank=True, verbose_name='OCR识别文字')
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'mistake_images'
        verbose_name = '错题图片'
        verbose_name_plural = '错题图片'

    def __str__(self):
        """返回图片描述作为字符串表示"""
        return f'{self.mistake.title} - {self.get_image_type_display()}'


class ReviewRecord(models.Model):
    """复习记录模型
    
    记录用户的错题复习情况
    """
    # 复习结果选择
    RESULT_CHOICES = [
        ('mastered', '已掌握'),
        ('wrong_again', '再次错误'),
    ]

    # 所属错题，级联删除
    mistake = models.ForeignKey(
        Mistake,
        on_delete=models.CASCADE,
        related_name='review_records',
        verbose_name='所属错题'
    )
    # 复习结果
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        verbose_name='复习结果'
    )
    # 复习笔记
    notes = models.TextField(blank=True, verbose_name='复习笔记')
    # 复习时间
    reviewed_at = models.DateTimeField(auto_now_add=True, verbose_name='复习时间')

    class Meta:
        db_table = 'review_records'
        verbose_name = '复习记录'
        verbose_name_plural = '复习记录'
        # 按复习时间倒序排列
        ordering = ['-reviewed_at']

    def __str__(self):
        """返回复习记录描述作为字符串表示"""
        return f'{self.mistake.title} - {self.get_result_display()}'


class ReviewImage(models.Model):
    """复习图片模型
    
    存储复习过程中上传的图片
    """
    # 所属复习记录，级联删除
    review_record = models.ForeignKey(
        ReviewRecord,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='所属复习记录'
    )
    # 图片文件
    image = models.ImageField(upload_to='review_images/', verbose_name='图片')
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'review_images'
        verbose_name = '复习图片'
        verbose_name_plural = '复习图片'

    def __str__(self):
        """返回图片描述作为字符串表示"""
        return f'{self.review_record} - 图片'


class PointsRecord(models.Model):
    """积分记录模型
    
    记录用户的积分变动情况
    """
    # 积分变动原因选择
    REASON_CHOICES = [
        ('review', '复习题目'),
        ('on_time_review', '按时复习'),
        ('early_review', '提前复习'),
        ('difficulty_bonus', '难度奖励'),
    ]

    # 关联用户，级联删除
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='points_records',
        verbose_name='用户'
    )
    # 积分变动值
    points = models.IntegerField(verbose_name='积分变动')
    # 变动原因
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        verbose_name='变动原因'
    )
    # 相关错题，可空
    mistake = models.ForeignKey(
        Mistake,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='points_records',
        verbose_name='相关错题'
    )
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'points_records'
        verbose_name = '积分记录'
        verbose_name_plural = '积分记录'
        # 按创建时间倒序排列
        ordering = ['-created_at']

    def __str__(self):
        """返回积分记录描述作为字符串表示"""
        return f'{self.user.username} - {self.points} 积分 - {self.get_reason_display()}'
