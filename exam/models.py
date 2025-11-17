from django.db import models
from django.contrib.auth.models import AbstractUser
import random

# User（ユーザー）
class User(AbstractUser):
    """カスタムユーザーモデル"""
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username

# ExamSet
class ExamSet(models.Model):
    """試験セット"""
    name = models.CharField(max_length=200, verbose_name="試験名")
    description = models.TextField(blank=True, verbose_name="説明")
    total_questions = models.IntegerField(default=40, verbose_name="問題数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "試験セット"
        verbose_name_plural = "試験セット"
    
    def __str__(self):
        return self.name

# Question（問題）
class Question(models.Model):
    """問題"""
    exam_set = models.ForeignKey(
        ExamSet, 
        on_delete=models.CASCADE, 
        related_name='questions',
        verbose_name="試験セット"
    )
    question_text = models.TextField(verbose_name="問題文")
    choice_1 = models.CharField(max_length=500, verbose_name="選択肢1")
    choice_2 = models.CharField(max_length=500, verbose_name="選択肢2")
    choice_3 = models.CharField(max_length=500, verbose_name="選択肢3")
    choice_4 = models.CharField(max_length=500, verbose_name="選択肢4")
    correct_answer = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')],
        verbose_name="正解番号"
    )
    explanation = models.TextField(verbose_name="解説")
    explanation_1 = models.TextField(verbose_name="選択肢1の説明")
    explanation_2 = models.TextField(verbose_name="選択肢2の説明")
    explanation_3 = models.TextField(verbose_name="選択肢3の説明")
    explanation_4 = models.TextField(verbose_name="選択肢4の説明")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "問題"
        verbose_name_plural = "問題"
    
    def __str__(self):
        return f"{self.exam_set.name} - {self.question_text[:50]}"
    
    def get_choices(self):
        """選択肢をリストで返す"""
        return [
            self.choice_1,
            self.choice_2,
            self.choice_3,
            self.choice_4
        ]
    
    def get_explanations(self):
        """各選択肢の説明をリストで返す"""
        return [
            self.explanation_1,
            self.explanation_2,
            self.explanation_3,
            self.explanation_4
        ]

# ExamSession（試験セッション）
class ExamSession(models.Model):
    """試験セッション（ユーザーの受験記録）"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='exam_sessions',
        verbose_name="ユーザー"
    )
    exam_set = models.ForeignKey(
        ExamSet, 
        on_delete=models.CASCADE,
        verbose_name="試験セット"
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="開始時刻")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完了時刻")
    score = models.IntegerField(null=True, blank=True, verbose_name="得点")
    total_questions = models.IntegerField(verbose_name="総問題数")
    is_completed = models.BooleanField(default=False, verbose_name="完了フラグ")
    
    class Meta:
        verbose_name = "試験セッション"
        verbose_name_plural = "試験セッション"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.exam_set.name} - {self.started_at}"
    
    def calculate_score(self):
        """得点を計算"""
        correct_count = self.answers.filter(is_correct=True).count()
        return correct_count
    
    def get_percentage(self):
        """正解率を計算"""
        if self.score is not None and self.total_questions > 0:
            return round((self.score / self.total_questions) * 100, 1)
        return 0

# answer（解答）
class Answer(models.Model):
    """解答記録"""
    session = models.ForeignKey(
        ExamSession, 
        on_delete=models.CASCADE, 
        related_name='answers',
        verbose_name="試験セッション"
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE,
        verbose_name="問題"
    )
    question_order = models.IntegerField(verbose_name="問題順序")
    user_answer = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')],
        verbose_name="ユーザーの解答"
    )
    is_correct = models.BooleanField(verbose_name="正解フラグ")
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="解答時刻")
    
    class Meta:
        verbose_name = "解答"
        verbose_name_plural = "解答"
        ordering = ['question_order']
    
    def __str__(self):
        return f"Q{self.question_order}: {'○' if self.is_correct else '×'}"