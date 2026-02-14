from django.contrib import admin
from .models import Subject, Group, KnowledgePoint, Mistake, MistakeImage, ReviewRecord


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'user', 'created_at']
    list_filter = ['subject', 'created_at']
    search_fields = ['name', 'user__username']


@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'user', 'created_at']
    list_filter = ['subject', 'created_at']
    search_fields = ['name', 'user__username']


@admin.register(Mistake)
class MistakeAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'user', 'error_cause', 'mastery_level', 'difficulty', 'created_at']
    list_filter = ['subject', 'error_cause', 'mastery_level', 'difficulty', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    filter_horizontal = ['knowledge_points']


@admin.register(MistakeImage)
class MistakeImageAdmin(admin.ModelAdmin):
    list_display = ['mistake', 'created_at']
    list_filter = ['created_at']


@admin.register(ReviewRecord)
class ReviewRecordAdmin(admin.ModelAdmin):
    list_display = ['mistake', 'result', 'reviewed_at']
    list_filter = ['result', 'reviewed_at']
