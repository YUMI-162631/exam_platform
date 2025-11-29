from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
import random
from .models import User, ExamSet, Question, ExamSession, Answer
from .forms import UserRegistrationForm, LoginForm

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

def login_view(request):
    """ログイン"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
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

@login_required
def user_logout(request):
    """ログアウト"""
    logout(request)
    messages.success(request, 'ログアウトしました。')
    return redirect('login')

@login_required
def top(request):
    """トップページ - 試験選択"""
    exam_sets = ExamSet.objects.all()
    
    # 中断中の試験セッションがあるかチェック
    incomplete_sessions = ExamSession.objects.filter(
        user=request.user,
        is_completed=False
    ).select_related('exam_set').order_by('-started_at')
    
    return render(request, 'exam/top.html', {
        'exam_sets': exam_sets,
        'incomplete_sessions': incomplete_sessions
    })

@login_required
def start_exam(request, exam_set_id):
    """試験開始"""
    exam_set = get_object_or_404(ExamSet, id=exam_set_id)
    
    # この試験セットで中断中のセッションがあるかチェック
    incomplete_session = ExamSession.objects.filter(
        user=request.user,
        exam_set=exam_set,
        is_completed=False
    ).first()
    
    if incomplete_session:
        # 中断中の試験がある場合
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'resume':
                # 再開する
                return redirect('resume_exam', session_id=incomplete_session.id)
            elif action == 'restart':
                # 既存のセッションを削除して新規開始
                incomplete_session.delete()
                # 新規開始のため、このまま処理を続行
            else:
                # キャンセルしてトップに戻る
                return redirect('top')
        else:
            # 確認画面を表示
            answered_count = incomplete_session.answers.count()
            return render(request, 'exam/confirm_restart.html', {
                'exam_set': exam_set,
                'incomplete_session': incomplete_session,
                'answered_count': answered_count
            })
    
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
    
    messages.success(request, '試験を開始しました。')
    return redirect('show_question')

@login_required
def resume_exam(request, session_id):
    """中断した試験を再開"""
    session = get_object_or_404(ExamSession, id=session_id, user=request.user, is_completed=False)
    
    # 既に解答済みの問題数を取得
    answered_count = session.answers.count()
    
    # 問題IDリストを復元（Answerから順番に取得）
    answered_questions = list(session.answers.order_by('question_order').values_list('question_id', flat=True))
    
    # 全問題を取得して復元
    all_questions = list(session.exam_set.questions.all())
    
    # 既に解答した問題のIDリストを作成
    if answered_questions:
        # 解答済みの問題を順番通りに配置
        question_ids = answered_questions.copy()
        
        # 残りの問題をランダムに追加
        remaining_questions = [q.id for q in all_questions if q.id not in answered_questions]
        needed_count = session.total_questions - len(question_ids)
        
        if remaining_questions and needed_count > 0:
            additional_questions = random.sample(
                remaining_questions, 
                min(needed_count, len(remaining_questions))
            )
            question_ids.extend(additional_questions)
    else:
        # まだ1問も解答していない場合は新規にランダム選択
        selected = random.sample(all_questions, session.total_questions)
        question_ids = [q.id for q in selected]
    
    # セッション情報を復元
    request.session['current_exam_session_id'] = session.id
    request.session['question_ids'] = question_ids
    request.session['current_question_index'] = answered_count
    
    messages.success(request, f'試験を再開します。（{answered_count}問解答済み）')
    return redirect('show_question')

@login_required
def show_question(request):
    """問題を1問ずつ表示"""
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
    
    # 既にこの問題に解答しているかチェック
    existing_answer = Answer.objects.filter(
        session=session,
        question=question
    ).first()
    
    context = {
        'session': session,
        'question': question,
        'current_number': current_index + 1,
        'total_questions': len(question_ids),
        'choices': enumerate(question.get_choices(), start=1),
        'is_first_question': current_index == 0,
        'previous_answer': existing_answer.user_answer if existing_answer else None,
    }
    
    return render(request, 'exam/question.html', context)

@login_required
def submit_answer(request):
    """解答を送信して次の問題へ"""
    if request.method != 'POST':
        return redirect('top')
    
    session_id = request.session.get('current_exam_session_id')
    question_ids = request.session.get('question_ids', [])
    current_index = request.session.get('current_question_index', 0)
    
    session = get_object_or_404(ExamSession, id=session_id)
    question = get_object_or_404(Question, id=question_ids[current_index])
    
    user_answer = int(request.POST.get('answer'))
    is_correct = (user_answer == question.correct_answer)
    
    # 既存の解答を更新または新規作成
    Answer.objects.update_or_create(
        session=session,
        question=question,
        defaults={
            'question_order': current_index + 1,
            'user_answer': user_answer,
            'is_correct': is_correct
        }
    )
    
    # 次の問題へ
    request.session['current_question_index'] = current_index + 1
    
    # 最後の問題なら結果画面へ
    if current_index + 1 >= len(question_ids):
        # スコア計算
        session.score = session.calculate_score()
        session.completed_at = timezone.now()
        session.is_completed = True
        session.save()
        
        return redirect('exam_result', session_id=session_id)
    
    # まだ問題があれば次の問題へ
    return redirect('show_question')

@login_required
def previous_question(request):
    """前の問題へ戻る"""
    current_index = request.session.get('current_question_index', 0)
    
    # 最初の問題より前には戻れない
    if current_index > 0:
        request.session['current_question_index'] = current_index - 1
    
    return redirect('show_question')

@login_required
def cancel_exam(request):
    """試験を中断してトップへ戻る、または途中で採点"""
    session_id = request.session.get('current_exam_session_id')
    
    if not session_id:
        return redirect('top')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'finish':
            # 途中で終了して採点
            session = get_object_or_404(ExamSession, id=session_id, user=request.user)
            
            # スコア計算（解答済みの問題のみ）
            session.score = session.calculate_score()
            session.completed_at = timezone.now()
            session.is_completed = True
            session.save()
            
            # セッション情報をクリア
            if 'current_exam_session_id' in request.session:
                del request.session['current_exam_session_id']
            if 'question_ids' in request.session:
                del request.session['question_ids']
            if 'current_question_index' in request.session:
                del request.session['current_question_index']
            
            messages.info(request, '試験を終了しました。解答済みの問題のみ採点します。')
            return redirect('exam_result', session_id=session_id)
        
        elif action == 'pause':
            # 中断して保存
            if 'current_exam_session_id' in request.session:
                del request.session['current_exam_session_id']
            if 'question_ids' in request.session:
                del request.session['question_ids']
            if 'current_question_index' in request.session:
                del request.session['current_question_index']
            
            messages.info(request, '試験を中断しました。続きから再開できます。')
            return redirect('top')
        
        else:
            # キャンセルして試験に戻る
            return redirect('show_question')
    
    # 確認画面を表示
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    answered_count = session.answers.count()
    current_index = request.session.get('current_question_index', 0)
    
    return render(request, 'exam/confirm_cancel.html', {
        'session': session,
        'answered_count': answered_count,
        'current_number': current_index + 1,
        'total_questions': session.total_questions
    })

@login_required
def delete_session(request, session_id):
    """中断したセッションを削除"""
    session = get_object_or_404(ExamSession, id=session_id, user=request.user, is_completed=False)
    session.delete()
    messages.success(request, '中断した試験を削除しました。')
    return redirect('top')

@login_required
def exam_result(request, session_id):
    """採点結果表示（40問分の解答を一覧表示）"""
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    
    # 解答一覧を取得（問題順に並べる）
    answers = session.answers.all().order_by('question_order')
    
    # 各解答に問題情報と選択肢を追加
    results = []
    for answer in answers:
        question = answer.question
        results.append({
            'number': answer.question_order,
            'question': question,
            'answer': answer,
            'choices_with_explanations': [
                (i, choice, explanation)
                for i, (choice, explanation) in enumerate(
                    zip(question.get_choices(), question.get_explanations()),
                    start=1
                )
            ]
        })
    
    # セッションデータをクリア
    if 'current_exam_session_id' in request.session:
        del request.session['current_exam_session_id']
    if 'question_ids' in request.session:
        del request.session['question_ids']
    if 'current_question_index' in request.session:
        del request.session['current_question_index']
    
    context = {
        'session': session,
        'results': results,
        'score': session.score,
        'total': session.total_questions,
        'percentage': session.get_percentage()
    }
    
    return render(request, 'exam/result.html', context)