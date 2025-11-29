from django.urls import path
from . import views

urlpatterns = [
    # 認証関連
    path('', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # トップページ
    path('top/', views.top, name='top'),
    
    # 試験関連
    path('exam/start/<int:exam_set_id>/', views.start_exam, name='start_exam'),
    path('exam/resume/<int:session_id>/', views.resume_exam, name='resume_exam'),
    path('exam/question/', views.show_question, name='show_question'),
    path('exam/submit/', views.submit_answer, name='submit_answer'),
    path('exam/previous/', views.previous_question, name='previous_question'),
    path('exam/cancel/', views.cancel_exam, name='cancel_exam'),
    path('exam/delete/<int:session_id>/', views.delete_session, name='delete_session'),
    path('exam/result/<int:session_id>/', views.exam_result, name='exam_result'),
]  