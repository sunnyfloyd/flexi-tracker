from django.urls.conf import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('issue/<int:pk>/', views.IssueDetailView.as_view(), name='issue_detail'),
    path('issue/<int:pk>/edit', views.IssueUpdateView.as_view(), name='issue_edit'),
    path('issues/', views.IssueListView.as_view(), name='issue_list'),
    path('new_issue/', views.IssueFormView.as_view(), name='new_issue'),
]
