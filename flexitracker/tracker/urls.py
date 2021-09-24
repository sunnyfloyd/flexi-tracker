from django.urls.conf import path
from . import views

app_name = "tracker"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("new_issue/", views.IssueCreateView.as_view(), name="new_issue"),
    path("issue/<int:pk>/", views.IssueDetailView.as_view(), name="issue_detail"),
    path("issue/<int:pk>/edit", views.IssueUpdateView.as_view(), name="issue_edit"),
    path("issue/<int:pk>/delete", views.IssueDeleteView.as_view(), name="issue_delete"),
    path("issue/<int:pk>/time_tracker/", views.time_tracker, name="time_tracker"),
    path("project/<int:pk>/issues/", views.IssueListView.as_view(), name="issue_list"),
    path("new_project/", views.ProjectCreateView.as_view(), name="new_project"),
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("project/<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path(
        "project/<int:pk>/edit/", views.ProjectUpdateView.as_view(), name="project_edit"
    ),
    path(
        "project/<int:pk>/delete/",
        views.ProjectDeleteView.as_view(),
        name="project_delete",
    ),
    path("user_timer_effort/", views.get_user_timer_effort, name="user_timer_effort"),
    path("search/", views.issue_search, name="issue_search"),
]
