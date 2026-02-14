from django.contrib import admin
from .models import SocraticSession, SocraticMessage, SimilarProblem, ReviewPlan


@admin.register(SocraticSession)
class SocraticSessionAdmin(admin.ModelAdmin):
    list_display = ['mistake', 'user', 'started_at', 'is_active']
    list_filter = ['is_active', 'started_at']
    search_fields = ['user__username', 'mistake__title']


@admin.register(SocraticMessage)
class SocraticMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'is_stuck_point', 'created_at']
    list_filter = ['role', 'is_stuck_point', 'created_at']


@admin.register(SimilarProblem)
class SimilarProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'original_mistake', 'user', 'difficulty', 'is_practiced', 'created_at']
    list_filter = ['difficulty', 'is_practiced', 'created_at']
    search_fields = ['title', 'user__username']


@admin.register(ReviewPlan)
class ReviewPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'mistake', 'scheduled_date', 'is_completed']
    list_filter = ['is_completed', 'scheduled_date']
    search_fields = ['user__username', 'mistake__title']
