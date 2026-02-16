from django.urls import path
from . import views

urlpatterns = [
    path('', views.mistake_list_view, name='mistake_list'),
    path('create/', views.mistake_create_view, name='mistake_create'),
    path('<int:pk>/', views.mistake_detail_view, name='mistake_detail'),
    path('<int:pk>/edit/', views.mistake_edit_view, name='mistake_edit'),
    path('<int:pk>/delete/', views.mistake_delete_view, name='mistake_delete'),
    path('<int:pk>/review/', views.review_mistake_view, name='review_mistake'),
    path('subjects/', views.subject_list_view, name='subject_list'),
    path('subjects/create/', views.subject_create_view, name='subject_create'),
    path('subjects/<int:pk>/delete/', views.subject_delete_view, name='subject_delete'),
]
