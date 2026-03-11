from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('announcement/<int:announcement_id>/', views.announcement_detail_view, name='announcement_detail'),
    # 教师相关路由
    path('teacher/dashboard/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('teacher/create-class/', views.create_class_view, name='create_class'),
    path('teacher/class-list/', views.class_list_view, name='class_list'),
    path('teacher/class/<int:class_id>/', views.class_detail_view, name='class_detail'),
    path('teacher/class/<int:class_id>/assign-student/', views.assign_student_view, name='assign_student'),
    path('teacher/class/<int:class_id>/remove-student/<int:student_id>/', views.remove_student_view, name='remove_student'),
    path('teacher/class/<int:class_id>/delete/', views.delete_class_view, name='delete_class'),
    # 学生管理路由
    path('teacher/student/<int:student_id>/review-plan/', views.student_review_plan_view, name='student_review_plan'),
    path('teacher/student/<int:student_id>/review-records/', views.student_review_records_view, name='student_review_records'),
    path('teacher/student/<int:student_id>/points/', views.student_points_view, name='student_points'),
]
