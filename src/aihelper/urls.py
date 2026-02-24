from django.urls import path
from . import views

urlpatterns = [
    path('review-plan/', views.review_plan_view, name='ai_review_plan'),
    path('socratic/<int:mistake_id>/', views.socratic_session_view, name='socratic_session'),
    path('socratic/<int:session_id>/end/', views.end_socratic_session_view, name='end_socratic_session'),
    path('similar/<int:mistake_id>/generate/', views.generate_similar_problem_view, name='generate_similar'),
    path('similar/<int:mistake_id>/', views.similar_problems_view, name='similar_problems'),
]
