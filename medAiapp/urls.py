from django.urls import path
from . import views
from . import views_lab

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('lab-dashboard/', views_lab.lab_dashboard, name='lab_dashboard'),
]