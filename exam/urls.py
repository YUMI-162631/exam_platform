from django.urls import path
from . import views

urlpatterns = [
    # 認証
    path('', views.top, name='top'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    # 試験
    path('exam/start/<int:exam_set_id>/', views.start_exam, name='start_exam'),
    path('exam/question/', views.show_question, name='show_question'),
    path('exam/submit/', views.submit_answer, name='submit_answer'),
    path('exam/answer/<int:question_id>/', views.show_answer_result, name='show_answer_result'),
    path('exam/next/', views.next_question, name='next_question'),
    path('exam/result/<int:session_id>/', views.exam_result, name='exam_result'),
]