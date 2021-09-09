from django.urls.conf import path
from . import views

app_name = "tracker"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("issue/<int:pk>/", views.IssueDetailView.as_view(), name="issue_detail"),
    path("issue/<int:pk>/edit", views.IssueUpdateView.as_view(), name="issue_edit"),
    path("<str:project>/issues/", views.IssueListView.as_view(), name="issue_list"),
    path("new_issue/", views.IssueCreateView.as_view(), name="new_issue"),
    path("new_project/", views.ProjectCreateView.as_view(), name="new_project"),
    path('<int:pk>/edit/', views.ProjectEditView.as_view(), name='project_edit'),
]
