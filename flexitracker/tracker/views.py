from django.contrib.auth import decorators
from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import generic
from .models import Issue, Project, TimeEntry
from .forms import IssueForm, ProjectForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.core.exceptions import BadRequest, PermissionDenied
from django.utils import timezone
from django.http import JsonResponse


class IndexView(generic.ListView):
    template_name = "tracker/dashboard.html"
    model = Issue
    paginate_by = 3

    def get_queryset(self):
        return self.request.user.profile.get_assigned_issues()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adding pagination
        per_page = context["paginator"].per_page
        page_obj = context["page_obj"]
        context["showing_first"] = per_page * (page_obj.number - 1) + 1
        context["showing_end"] = context["showing_first"] + len(page_obj) - 1
        return context


class IssueDetailView(generic.DetailView):
    template_name = "tracker/issue_detail.html"
    model = Issue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = Issue.objects.get(pk=self.kwargs["pk"]).project.pk
        return context


class IssueListView(generic.ListView):
    template_name = "tracker/issue_list.html"
    model = Issue
    paginate_by = 3

    def get_queryset(self):
        self.project = get_object_or_404(Project, pk=self.kwargs["pk"])
        return Issue.objects.filter(project=self.project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = self.project

        # Adding pagination
        per_page = context["paginator"].per_page
        page_obj = context["page_obj"]
        context["showing_first"] = per_page * (page_obj.number - 1) + 1
        context["showing_end"] = context["showing_first"] + len(page_obj) - 1
        return context


class IssueCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "tracker/issue_form.html"
    form_class = IssueForm
    site_name = "Issue Form"

    def form_valid(self, form):
        issue = form.save(commit=False)
        issue.creator = self.request.user
        return super().form_valid(form)


class IssueUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "tracker/issue_form.html"
    form_class = IssueForm
    model = Issue

    def form_valid(self, form):
        issue = form.save(commit=False)
        issue.last_update_by = self.request.user
        return super().form_valid(form)


class ProjectListView(LoginRequiredMixin, generic.ListView):
    template_name = "tracker/project_list.html"
    model = Project

    def get_queryset(self):
        return Project.objects.filter(creator=self.request.user)


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "tracker/project_detail.html"
    model = Project


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "tracker/project_form.html"
    form_class = ProjectForm

    def form_valid(self, form):
        project = form.save(commit=False)
        project.creator = self.request.user
        return super().form_valid(form)


class ProjectEditView(LoginRequiredMixin, generic.UpdateView):
    template_name = "tracker/project_form.html"
    form_class = ProjectForm
    model = Project

    def form_valid(self, form):
        project = form.save(commit=False)
        project.last_update_by = self.request.user
        return super().form_valid(form)


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    success_url = reverse_lazy("tracker:project_list")

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        project = Project.objects.get(pk=pk)
        project.last_update_by = self.request.user
        project.save()
        return super().delete(request, *args, **kwargs)


@login_required
@require_http_methods(["POST"])
def time_tracker(request, pk, action):
    issue = get_object_or_404(Issue, pk=pk)
    if action.lower() == "start":
        if request.user.profile.has_running_timer:
            raise PermissionDenied("You cannot have multiple running time trackers.")
        TimeEntry.objects.create(user=request.user, issue=issue)
        return JsonResponse({"message": "Timer has successfully started."}, status=201)

    if action.lower() == "stop":
        # te = request.user.profile.time_entries.get(user=request.user, issue=issue, end_time=None)
        time_entry = get_object_or_404(
            request.user.time_entries,
            user=request.user,
            issue=issue,
            end_time=None,
        )
        time_entry.end_time = timezone.now()
        time_entry.save()
        return JsonResponse({"message": "Timer has successfully stopped."}, status=200)

    else:
        return BadRequest("Requested action is not recognized.")
