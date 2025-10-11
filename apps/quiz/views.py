import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .models import Question, Answer

SESSION_KEY_QUESTIONS = 'quiz_questions'
SESSION_KEY_ANSWERS = 'quiz_answers'
QUESTIONS_COUNT = 5 # Количество вопросов в одном тесте

def quiz_start_view(request: HttpRequest) -> HttpResponse:
    # Получаем случайные ID вопросов
    question_ids = list(Question.objects.values_list('id', flat=True))
    
    if len(question_ids) < QUESTIONS_COUNT:
        # Обработка случая, когда вопросов в базе меньше, чем нужно
        return render(request, 'quiz/quiz_not_enough_questions.html', {'required_count': QUESTIONS_COUNT})
    
    selected_ids = random.sample(question_ids, QUESTIONS_COUNT)
    
    # Сохраняем ID в сессию и очищаем предыдущие ответы
    request.session[SESSION_KEY_QUESTIONS] = selected_ids
    request.session[SESSION_KEY_ANSWERS] = {}
    
    # Перенаправляем на первый вопрос
    first_question_id = selected_ids[0]
    return redirect('quiz:question', question_id=first_question_id)


def question_view(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, id=question_id)
    question_ids = request.session.get(SESSION_KEY_QUESTIONS, [])
    
    if question_id not in question_ids:
        # Если пытаются получить доступ к вопросу не из текущего теста
        return redirect('quiz:start')
        
    current_index = question_ids.index(question_id)
    progress = int(((current_index) / len(question_ids)) * 100)
    
    context = {
        'question': question,
        'progress': progress,
    }
    return render(request, 'quiz/question.html', context)


def check_answer_view(request: HttpRequest, question_id: int) -> HttpResponse:
    if request.method != 'POST':
        return redirect('quiz:question', question_id=question_id)

    question = get_object_or_404(Question, id=question_id)
    selected_answer_id = request.POST.get('answer')
    
    if not selected_answer_id:
        # Если ответ не был выбран
        # Можно добавить сообщение об ошибке через Django Messages Framework
        return redirect('quiz:question', question_id=question_id)

    # Сохраняем ответ пользователя в сессию
    user_answers = request.session.get(SESSION_KEY_ANSWERS, {})
    user_answers[str(question_id)] = int(selected_answer_id)
    request.session[SESSION_KEY_ANSWERS] = user_answers
    
    # Определяем следующий вопрос или переходим к результатам
    question_ids = request.session.get(SESSION_KEY_QUESTIONS, [])
    current_index = question_ids.index(question_id)
    
    if current_index + 1 < len(question_ids):
        next_question_id = question_ids[current_index + 1]
        return redirect('quiz:question', question_id=next_question_id)
    else:
        return redirect('quiz:results')


def quiz_results_view(request: HttpRequest) -> HttpResponse:
    question_ids = request.session.get(SESSION_KEY_QUESTIONS, [])
    user_answers_map = request.session.get(SESSION_KEY_ANSWERS, {})

    if not question_ids or not user_answers_map:
        return redirect('quiz:start')

    questions = Question.objects.filter(id__in=question_ids).prefetch_related('answers')
    
    results = []
    correct_count = 0
    
    for q_id in question_ids:
        question = next((q for q in questions if q.id == q_id), None)
        if not question: continue

        user_answer_id = user_answers_map.get(str(q_id))
        user_answer = next((a for a in question.answers.all() if a.id == user_answer_id), None)
        correct_answer = next((a for a in question.answers.all() if a.is_correct), None)
        
        is_correct = user_answer and user_answer.is_correct
        if is_correct:
            correct_count += 1
            
        results.append({
            'question': question,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
        })
    
    score = (correct_count / len(question_ids)) * 100 if question_ids else 0
    
    context = {
        'results': results,
        'correct_count': correct_count,
        'total_questions': len(question_ids),
        'score': round(score, 2),
    }
    
    # Очищаем сессию после показа результатов
    request.session.pop(SESSION_KEY_QUESTIONS, None)
    request.session.pop(SESSION_KEY_ANSWERS, None)
    
    return render(request, 'quiz/results.html', context)
