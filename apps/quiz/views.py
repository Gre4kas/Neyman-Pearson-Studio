from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Quiz, Question, QuizResult

def get_session_keys(quiz_id):
    return f'quiz_{quiz_id}_questions', f'quiz_{quiz_id}_answers'

def quiz_list_view(request: HttpRequest) -> HttpResponse:
    quizzes = Quiz.objects.all()
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})

def quiz_start_view(request: HttpRequest, quiz_id: int) -> HttpResponse:
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question_ids = list(quiz.questions.values_list('id', flat=True))

    if not question_ids:
        return render(request, 'quiz/quiz_not_enough_questions.html', {'quiz': quiz})
    
    # Ключи сессии теперь уникальны для каждого теста
    questions_key, answers_key = get_session_keys(quiz_id)

    request.session[questions_key] = question_ids
    request.session[answers_key] = {}
    
    first_question_id = question_ids[0]
    return redirect('quiz:question', quiz_id=quiz_id, question_id=first_question_id)

def question_view(request: HttpRequest, quiz_id: int, question_id: int) -> HttpResponse:
    questions_key, _ = get_session_keys(quiz_id)
    question_ids = request.session.get(questions_key, [])
    
    if question_id not in question_ids:
        return redirect('quiz:list')

    question = get_object_or_404(Question, id=question_id)
    current_index = question_ids.index(question_id)
    progress = int(((current_index) / len(question_ids)) * 100)
    
    context = {
        'quiz_id': quiz_id,
        'question': question,
        'progress': progress,
    }
    return render(request, 'quiz/question.html', context)

def check_answer_view(request: HttpRequest, quiz_id: int, question_id: int) -> HttpResponse:
    if request.method != 'POST':
        return redirect('quiz:question', quiz_id=quiz_id, question_id=question_id)
    
    questions_key, answers_key = get_session_keys(quiz_id)
    
    # Используем getlist для получения всех выбранных чекбоксов
    selected_answer_ids = request.POST.getlist('answer')
    
    user_answers = request.session.get(answers_key, {})
    # Сохраняем список ID ответов, преобразованных в int
    user_answers[str(question_id)] = [int(aid) for aid in selected_answer_ids]
    request.session[answers_key] = user_answers
    
    question_ids = request.session.get(questions_key, [])
    current_index = question_ids.index(question_id)
    
    if current_index + 1 < len(question_ids):
        next_question_id = question_ids[current_index + 1]
        return redirect('quiz:question', quiz_id=quiz_id, question_id=next_question_id)
    else:
        return redirect('quiz:results', quiz_id=quiz_id)

def quiz_results_view(request: HttpRequest, quiz_id: int) -> HttpResponse:
    questions_key, answers_key = get_session_keys(quiz_id)
    question_ids = request.session.get(questions_key, [])
    user_answers_map = request.session.get(answers_key, {})

    if not question_ids:
        return redirect('quiz:list')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(id__in=question_ids).prefetch_related('answers')
    
    results = []
    correct_count = 0
    total_questions = len(question_ids)
    
    for question in questions:
        user_answer_ids = set(user_answers_map.get(str(question.id), []))
        correct_answer_ids = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
        
        is_correct = (user_answer_ids == correct_answer_ids)
        if is_correct:
            correct_count += 1
            
        results.append({
            'question': question,
            'user_answers': question.answers.filter(id__in=user_answer_ids),
            'correct_answers': question.answers.filter(is_correct=True),
            'is_correct': is_correct,
        })

    score = (correct_count / total_questions) * 100 if total_questions else 0

    if request.user.is_authenticated:
        QuizResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=round(score, 2)
        )

    context = {
        'quiz': quiz,
        'results': results,
        'correct_count': correct_count,
        'total_questions': total_questions,
        'score': round(score, 2),
    }
    
    # Очищаем сессию
    request.session.pop(questions_key, None)
    request.session.pop(answers_key, None)
    
    return render(request, 'quiz/results.html', context)


@login_required
def quiz_history_view(request: HttpRequest) -> HttpResponse:
    results_list = QuizResult.objects.filter(user=request.user) \
                                     .select_related('quiz') \
                                     .order_by('-completed_at')
    
    # Пагинация
    page = request.GET.get('page', 1)
    paginator = Paginator(results_list, 10) # 10 элементов на страницу
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    
    context = {
        'results': results
    }
    return render(request, 'quiz/history.html', context)
