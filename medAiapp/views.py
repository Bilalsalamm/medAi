
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login

def home(request):
    return render(request, 'homepage.html')

def dashboard(request):
    # This is where you'll eventually pull data from your database
    return render(request, 'dashboard.html')

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            error = 'Invalid username or password.'
    return render(request, 'login.html', {'error': error})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Here you would implement sending a reset email
        return render(request, 'forgot_password.html', {'message': 'If this email exists, a reset link has been sent.'})
    return render(request, 'forgot_password.html')

def register(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            error = 'Username already exists.'
        else:
            User.objects.create_user(username=username, password=password, email=email)
            return redirect('login')
    return render(request, 'register.html', {'error': error})