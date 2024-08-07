from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('email_sent/', views.email_sent, name='email_sent'),
]
