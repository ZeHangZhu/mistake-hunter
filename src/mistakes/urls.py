from django.urls import path
from . import views

urlpatterns = [
    path('', views.mistake_list_view, name='mistake_list'),
    path('create/', views.mistake_create_view, name='mistake_create'),
    path('<int:pk>/', views.mistake_detail_view, name='mistake_detail'),
    path('<int:pk>/edit/', views.mistake_edit_view, name='mistake_edit'),
    path('<int:pk>/delete/', views.mistake_delete_view, name='mistake_delete'),
    path('<int:pk>/review/', views.review_mistake_view, name='review_mistake'),
    path('review_plan/', views.generate_review_plan_view, name='review_plan'),
    path('review_plan', views.generate_review_plan_view, name='review_plan_no_slash'),
    path('review_plan/export/', views.export_review_plan_doc, name='export_review_plan_doc'),
    path('review_records/', views.review_records_view, name='review_records'),
    path('subjects/', views.subject_list_view, name='subject_list'),
    path('subjects/create/', views.subject_create_view, name='subject_create'),
    path('subjects/<int:pk>/delete/', views.subject_delete_view, name='subject_delete'),
    path('points_center/', views.points_center_view, name='points_center'),
    path('analytics/', views.analytics_view, name='analytics'),
]
