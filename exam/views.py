from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
import random
from .models import User, ExamSet, Question, ExamSession, Answer
from .forms import UserRegistrationForm, LoginForm

# egister（ユーザー登録）
def register(request):
    """ユーザー登録"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, 'アカウントが作成されました！')
            return redirect('top')
    else:
        form = UserRegistrationForm()
    return render(request, 'exam/register.html', {'form': form})

# login_view（ログイン）
def login_view(request):
    """ログイン"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # メールアドレスでユーザーを検索
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('top')
                else:
                    messages.error(request, 'メールアドレスまたはパスワードが正しくありません。')
            except User.DoesNotExist:
                messages.error(request, 'メールアドレスまたはパスワードが正しくありません。')
    else:
        form = LoginForm()
    return render(request, 'exam/login.html', {'form': form})

#user_logout（ログアウト）
@login_required
def user_logout(request):
    """ログアウト"""
    logout(request)
    messages.success(request, 'ログアウトしました。')
    return redirect('login')

# top（トップページ）
@login_required
def top(request):
    """トップページ - 試験選択"""
    exam_sets = ExamSet.objects.all()
    return render(request, 'exam/top.html', {'exam_sets': exam_sets})

# start_exam（試験開始）
@login_required
def start_exam(request, exam_set_id):
    """試験開始"""
    exam_set = get_object_or_404(ExamSet, id=exam_set_id)
    
    # 問題が十分にあるか確認
    questions = list(exam_set.questions.all())
    if len(questions) < exam_set.total_questions:
        messages.error(request, f'この試験には問題が不足しています。（現在{len(questions)}問）')
        return redirect('top')
    
    # ランダムに問題を選択
    selected_questions = random.sample(questions, exam_set.total_questions)
    
    # 試験セッションを作成
    with transaction.atomic():
        session = ExamSession.objects.create(
            user=request.user,
            exam_set=exam_set,
            total_questions=exam_set.total_questions
        )
        
        # セッションIDと問題IDリストをセッションに保存
        request.session['current_exam_session_id'] = session.id
        request.session['question_ids'] = [q.id for q in selected_questions]
        request.session['current_question_index'] = 0
    
    return redirect('show_question')

# show_question（問題表示）
@login_required
def show_question(request):
    """問題表示"""
    session_id = request.session.get('current_exam_session_id')
    question_ids = request.session.get('question_ids', [])
    current_index = request.session.get('current_question_index', 0)
    
    if not session_id or not question_ids:
        messages.error(request, '試験セッションが見つかりません。')
        return redirect('top')
    
    if current_index >= len(question_ids):
        return redirect('exam_result', session_id=session_id)
    
    session = get_object_or_404(ExamSession, id=session_id)
    question = get_object_or_404(Question, id=question_ids[current_index])
    
    context = {
        'session': session,
        'question': question,
        'current_number': current_index + 1,
        'total_questions': len(question_ids),
        'choices': enumerate(question.get_choices(), start=1)
    }
    
    return render(request, 'exam/question.html', context)

# submit_answer（解答送信）
@login_required
def submit_answer(request):
    """解答送信"""
    if request.method != 'POST':
        return redirect('top')
    
    session_id = request.session.get('current_exam_session_id')
    question_ids = request.session.get('question_ids', [])
    current_index = request.session.get('current_question_index', 0)
    
    session = get_object_or_404(ExamSession, id=session_id)
    question = get_object_or_404(Question, id=question_ids[current_index])
    
    user_answer = int(request.POST.get('answer'))
    is_correct = (user_answer == question.correct_answer)
    
    # 解答を保存
    Answer.objects.create(
        session=session,
        question=question,
        question_order=current_index + 1,
        user_answer=user_answer,
        is_correct=is_correct
    )
    
    return redirect('show_answer_result', question_id=question.id)

# show_answer_result（解答結果表示）
@login_required
def show_answer_result(request, question_id):
    """解答結果表示"""
    session_id = request.session.get('current_exam_session_id')
    current_index = request.session.get('current_question_index', 0)
    question_ids = request.session.get('question_ids', [])
    
    session = get_object_or_404(ExamSession, id=session_id)
    question = get_object_or_404(Question, id=question_id)
    answer = Answer.objects.get(
        session=session,
        question=question,
        question_order=current_index + 1
    )
    
    choices_with_explanations = [
        (i, choice, explanation)
        for i, (choice, explanation) in enumerate(
            zip(question.get_choices(), question.get_explanations()),
            start=1
        )
    ]
    
    context = {
        'question': question,
        'answer': answer,
        'current_number': current_index + 1,
        'total_questions': len(question_ids),
        'choices_with_explanations': choices_with_explanations,
        'is_last_question': current_index >= len(question_ids) - 1
    }
    
    return render(request, 'exam/answer_result.html', context)

# next_question（次の問題へ）
@login_required
def next_question(request):
    """次の問題へ"""
    current_index = request.session.get('current_question_index', 0)
    question_ids = request.session.get('question_ids', [])
    
    request.session['current_question_index'] = current_index + 1
    
    if current_index + 1 >= len(question_ids):
        # 全問題終了
        session_id = request.session.get('current_exam_session_id')
        session = get_object_or_404(ExamSession, id=session_id)
        
        # スコア計算
        session.score = session.calculate_score()
        session.completed_at = timezone.now()
        session.is_completed = True
        session.save()
        
        return redirect('exam_result', session_id=session_id)
    
    return redirect('show_question')

# exam_result（試験結果表示）
@login_required
def exam_result(request, session_id):
    """試験結果表示"""
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    
    # セッションデータをクリア
    if 'current_exam_session_id' in request.session:
        del request.session['current_exam_session_id']
    if 'question_ids' in request.session:
        del request.session['question_ids']
    if 'current_question_index' in request.session:
        del request.session['current_question_index']
    
    context = {
        'session': session,
        'score': session.score,
        'total': session.total_questions,
        'percentage': session.get_percentage()
    }
    
    return render(request, 'exam/result.html', context)
