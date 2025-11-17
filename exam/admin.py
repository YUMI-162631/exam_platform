from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ExamSet, Question, ExamSession, Answer

# カスタムユーザーモデルを管理画面に登録
admin.site.register(User, UserAdmin)

# 試験セット一覧に表示する項目
@admin.register(ExamSet)
class ExamSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_questions', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

# 問題一覧に表示する項目
# 検索、フィルター機能も追加
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['get_exam_name', 'get_question_preview', 'correct_answer', 'created_at']
    list_filter = ['exam_set', 'created_at']
    search_fields = ['question_text']
    
    def get_exam_name(self, obj):
        return obj.exam_set.name
    get_exam_name.short_description = '試験名'
    
    def get_question_preview(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    get_question_preview.short_description = '問題文'

# 試験セッション管理
@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam_set', 'score', 'total_questions', 'get_percentage', 'is_completed', 'started_at']
    list_filter = ['exam_set', 'is_completed', 'started_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['started_at', 'completed_at']
    
    def get_percentage(self, obj):
        return f"{obj.get_percentage()}%"
    get_percentage.short_description = '正解率'
    
# 解答記録管理
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'get_exam', 'question_order', 'is_correct', 'answered_at']
    list_filter = ['is_correct', 'answered_at']
    search_fields = ['session__user__username']
    readonly_fields = ['answered_at']
    
    def get_user(self, obj):
        return obj.session.user.username
    get_user.short_description = 'ユーザー'
    
    def get_exam(self, obj):
        return obj.session.exam_set.name
    get_exam.short_description = '試験'
