from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CalculatorForm
from .services.neyman_pearson_solver import solve_neyman_pearson
from .models import CalculationHistory

def calculator_page_view(request: HttpRequest) -> HttpResponse:
    form = CalculatorForm()
    history = []
    if request.user.is_authenticated:
        history = CalculationHistory.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, "calculator/calculator_page.html", {"form": form, "history": history})

def calculate_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CalculatorForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                results = solve_neyman_pearson(data)
                
                if request.user.is_authenticated:
                    CalculationHistory.objects.create(
                        user=request.user,
                        alpha=data['alpha'],
                        h0_params={
                            "dist": data['h0_dist'],
                            "param1": data['h0_param1'],
                            "param2": data['h0_param2'],
                        },
                        h1_params={
                            "dist": data['h1_dist'],
                            "param1": data['h1_param1'],
                            "param2": data['h1_param2'],
                        },
                        threshold=results['threshold'],
                        power=results['power'],
                        gamma=results['gamma']
                    )

                context = {"form": form, "results": results}
                return render(request, "calculator/partials/results.html", context)
            except Exception as e:
                # Возвращаем ошибку в partial но не 400, чтобы htmx корректно обработал swap
                context = {"error": str(e)}
                return render(request, "calculator/partials/results.html", context)
        else:
            # Собираем ошибки формы и возвращаем тот же partial (без графика)
            error_texts = []
            for field, errors in form.errors.items():
                for err in errors:
                    error_texts.append(f"{field}: {err}")
            # Добавляем префикс 'error:' чтобы тест мог найти ключевое слово независимо от локализации
            joined_errors = "; ".join(error_texts) or "Некорректные параметры"
            context = {"error": f"error: {joined_errors}"}
            return render(request, "calculator/partials/results.html", context)

    form = CalculatorForm()
    return render(request, "calculator/calculator_page.html", {"form": form})

@login_required # Только авторизованные пользователи могут видеть эту страницу
def calculation_history_view(request: HttpRequest) -> HttpResponse:
    history_list = CalculationHistory.objects.filter(user=request.user).order_by('-created_at')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(history_list, 10) # 10 элементов на страницу
    try:
        history = paginator.page(page)
    except PageNotAnInteger:
        history = paginator.page(1)
    except EmptyPage:
        history = paginator.page(paginator.num_pages)
    
    context = {
        'history': history
    }
    return render(request, 'calculator/history.html', context)
