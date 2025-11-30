from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from .forms import CalculatorForm
from .services.neyman_pearson_solver import solve_neyman_pearson
from .models import CalculationHistory

def calculator_page_view(request: HttpRequest) -> HttpResponse:
    """Відображення сторінки калькулятора."""
    form = CalculatorForm()
    history = []
    if request.user.is_authenticated:
        history = CalculationHistory.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, "calculator/calculator_page.html", {"form": form, "history": history})

def calculate_view(request: HttpRequest) -> HttpResponse:
    """Обробка HTMX запиту на розрахунок."""
    if request.method == "POST":
        form = CalculatorForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                # Виклик солвера
                results = solve_neyman_pearson(data)
                
                # Збереження в історію
                if request.user.is_authenticated:
                    CalculationHistory.objects.create(
                        user=request.user,
                        threshold=results['controlled_limit'],
                        power=results['best_value'],
                        extra_data={
                            "matrix": results['matrix'],
                            "probabilities": results['full_probabilities'],
                            "controlled_col": results['controlled_col'],
                            "solution_type": "Mixed" if results['is_mixed'] else "Pure"
                        }
                    )

                context = {"results": results}
                return render(request, "calculator/partials/results.html", context)
            
            except Exception as e:
                return render(request, "calculator/partials/results.html", {"error": str(e)})
        else:
            # Формування тексту помилок
            error_texts = [f"{field}: {', '.join(err)}" for field, err in form.errors.items()]
            context = {"error": "; ".join(error_texts)}
            return render(request, "calculator/partials/results.html", context)

    return HttpResponse(status=405)

@login_required
def calculation_history_view(request: HttpRequest) -> HttpResponse:
    """Сторінка повної історії."""
    history_list = CalculationHistory.objects.filter(user=request.user).order_by('-created_at')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(history_list, 10)
    
    try:
        history = paginator.page(page)
    except PageNotAnInteger:
        history = paginator.page(1)
    except EmptyPage:
        history = paginator.page(paginator.num_pages)
    
    return render(request, 'calculator/history.html', {'history': history})