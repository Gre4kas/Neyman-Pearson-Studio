from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from .forms import UserRegisterForm, EmailOrUsernameAuthenticationForm

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


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = EmailOrUsernameAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Неверное имя пользователя/email или пароль.')
    else:
        form = EmailOrUsernameAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('home')
