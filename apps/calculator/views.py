from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from .forms import CalculatorForm
from .services.neyman_pearson_solver import solve_neyman_pearson

def calculator_page_view(request: HttpRequest) -> HttpResponse:
    form = CalculatorForm()
    return render(request, "calculator/calculator_page.html", {"form": form})

def calculate_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CalculatorForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                # Call the core logic service
                results = solve_neyman_pearson(data)
                context = {
                    "form": form,
                    "results": results,
                }
                # Use a partial template for HTMX
                return render(request, "calculator/partials/results.html", context)
            except Exception as e:
                context = {"error": str(e)}
                return render(request, "calculator/partials/results.html", context, status=400)

    # Fallback for non-POST or invalid form for non-HTMX requests (optional)
    form = CalculatorForm()
    return render(request, "calculator/calculator_page.html", {"form": form})