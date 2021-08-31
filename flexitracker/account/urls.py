from django.urls import path
from django.urls.conf import include
from . import views

app_name = 'account'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.RegistrationForm.as_view(), name='register'),
    path('register_done/', views.register_done, name='register_done'),
]
