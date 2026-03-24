
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
def logout_view(request):
    auth_logout(request)
    return redirect('login')

def home(request):
    return render(request, 'homepage.html')

def dashboard(request):
    user = request.user
    return render(request, 'dashboard.html', {'user': user})

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Redirect based on user role
            try:
                role = user.userprofile.role
                if role == 'lab_assistant':
                    return redirect('lab_dashboard')
                elif role == 'doctor':
                    return redirect('dashboard')  # Replace with doctor_dashboard if you have one
                else:
                    return redirect('dashboard')
            except Exception:
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

from .models import PendingUser

def register(request):
    error = None
    message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists() or PendingUser.objects.filter(username=username).exists():
            error = 'Username already exists or is pending approval.'
        elif User.objects.filter(email=email).exists() or PendingUser.objects.filter(email=email).exists():
            error = 'Email already exists or is pending approval.'
        else:
            PendingUser.objects.create(username=username, password=password, email=email)
            message = 'Registration submitted. Awaiting admin approval.'
    return render(request, 'register.html', {'error': error, 'message': message})