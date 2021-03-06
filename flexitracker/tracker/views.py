from django.shortcuts import get_object_or_404
from django.views import generic
from .models import Issue, Project, TimeEntry
from .forms import IssueForm, ProjectForm, SearchForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.http import JsonResponse
import json
from guardian.mixins import PermissionRequiredMixin
from .utils import add_pagination_context
from .custom_mixins import LogDeletionMixin, ProjectContextMixin, TrackerFormMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = "tracker/dashboard.html"
    model = Issue
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.profile.get_assigned_issues()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_pagination_context(context)


################## ISSUE VIEWS ##################
class IssueDetailView(PermissionRequiredMixin, generic.DetailView, ProjectContextMixin):
    template_name = "tracker/issue_detail.html"
    model = Issue
    permission_required = "view_project"

    def get_permission_object(self):
        return Issue.objects.get(pk=self.kwargs["pk"]).project


class IssueListView(PermissionRequiredMixin, generic.ListView, ProjectContextMixin):
    template_name = "tracker/issue_list.html"
    model = Project
    paginate_by = 10
    permission_required = "view_project"

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        return Issue.objects.filter(project=project)

    def get_permission_object(self):
        return get_object_or_404(Project, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        context["project"] = project
        return add_pagination_context(context)


class IssueCreateView(LoginRequiredMixin, generic.CreateView, TrackerFormMixin):
    template_name = "tracker/issue_form.html"
    form_class = IssueForm


class IssueUpdateView(
    PermissionRequiredMixin, generic.UpdateView, TrackerFormMixin, ProjectContextMixin
):
    template_name = "tracker/issue_form.html"
    model = Issue
    form_class = IssueForm
    permission_required = "change_project_issue"
    is_update = True

    def get_permission_object(self):
        issue = get_object_or_404(Issue, pk=self.kwargs["pk"])
        return issue.project


class IssueDeleteView(
    PermissionRequiredMixin, generic.DeleteView, LogDeletionMixin, ProjectContextMixin
):
    model = Issue
    permission_required = "delete_issue"

    def get_success_url(self):
        project = Issue.objects.get(pk=self.kwargs["pk"]).project
        return project.get_absolute_url()


################## PROJECT VIEWS ##################
class ProjectListView(LoginRequiredMixin, generic.ListView):
    template_name = "tracker/project_list.html"
    model = Project

    def get_queryset(self):
        return Project.objects.filter(creator=self.request.user)


class ProjectDetailView(
    PermissionRequiredMixin, generic.DetailView, ProjectContextMixin
):
    template_name = "tracker/project_detail.html"
    model = Project
    permission_required = "view_project"


class ProjectCreateView(LoginRequiredMixin, generic.CreateView, TrackerFormMixin):
    template_name = "tracker/project_form.html"
    form_class = ProjectForm


class ProjectUpdateView(
    PermissionRequiredMixin, generic.UpdateView, TrackerFormMixin, ProjectContextMixin
):
    template_name = "tracker/project_form.html"
    model = Project
    form_class = ProjectForm
    permission_required = "change_project"
    is_update = True


class ProjectDeleteView(
    PermissionRequiredMixin, generic.DeleteView, LogDeletionMixin, ProjectContextMixin
):
    model = Project
    success_url = reverse_lazy("tracker:project_list")
    permission_required = "delete_project"


################## SEARCH VIEW ##################
@login_required
def issue_search(request):
    """
    View returning list of issues that match given query based on Trigram Similarity.

    Requires pg_trgm extension to be installed on a PostgreSQL database.
    """
    query = None
    results = []
    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            trigram = (
                TrigramSimilarity("name", query)
                + TrigramSimilarity("description", query)
            )
            user_project_scope = (
                Q(project__in=request.user.projects.all())
                | Q(project__in=request.user.created_projects.all())
            )
            results = (
                Issue.objects.annotate(similarity=trigram)
                .filter(Q(similarity__gt=0.1), user_project_scope)
                .order_by("-similarity")
            )
            paginator = Paginator(results, 10)
            page = request.GET.get('page')
            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
        context = {
            "paginator": paginator,
            "page_obj": page_obj,
            "query": query,
            "query_url": f"query={query}&"
        }
    return render(
        request,
        "tracker/search.html",
        add_pagination_context(context),
    )


################## AJAX API ##################
@login_required
@require_http_methods(["POST"])
def time_tracker(request, pk):
    """
    This view allows for starting and stopping work timer for a logged user
    and returns logged work effort in seconds.
    """
    issue = Issue.objects.get(pk=pk)
    if not issue:
        return JsonResponse({"message": "There is no issue with this ID."}, status=404)
    data = json.loads(request.body)
    action = data["action"]

    if action.lower() == "start":
        if request.user.profile.has_running_timer:
            return JsonResponse(
                {"message": "You cannot have multiple running timers."},
                status=403,
            )
        TimeEntry.objects.create(user=request.user, issue=issue)
        return JsonResponse(
            {"work_effort_actual": issue.work_effort_actual}, status=200
        )

    if action.lower() != "stop":
        return JsonResponse(
            {"message": "Requested action is not recognized."}, status=400
        )

    time_entry = request.user.time_entries.get(
        user=request.user, issue=issue, end_time=None
    )
    if not time_entry:
        return JsonResponse(
            {"message": "Current user does not have a running timer."}, status=404
        )
    time_entry.end_time = timezone.now()
    time_entry.save()
    return JsonResponse({"work_effort_actual": issue.work_effort_actual}, status=200)


# @login_required
@require_http_methods(["GET"])
def get_user_timer_effort(request):
    """
    This view returns work effort in seconds clocked on current user's running timer
    if user has one.
    """
    if request.user.profile.has_running_timer:
        time_entry = request.user.time_entries.get(user=request.user, end_time=None)
        return JsonResponse({"work_effort": time_entry.work_effort}, status=200)
    else:
        return JsonResponse(
            {"message": "Current user does not have a running timer."}, status=200
        )
