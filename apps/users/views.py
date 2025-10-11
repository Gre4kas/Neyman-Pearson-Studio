from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from .forms import UserRegisterForm

def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически входим в систему после успешной регистрации
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})
