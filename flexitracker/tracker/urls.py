from django.urls.conf import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
