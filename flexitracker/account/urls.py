from django.urls import path
from django.urls.conf import include
from . import views

app_name = 'account'

urlpatterns = [
    path('', views.profile_user, name='profile_user'),
    path('<int:pk>/', views.profile, name='profile'),
    path('password_change/', views.PasswordChangeAccountView.as_view(), name='password_change'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.RegistrationFormView.as_view(), name='register'),
    path('register_done/', views.register_done, name='register_done'),
]
