from django.shortcuts import get_object_or_404, render
from django.views import generic
from .models import Issue, Project, TimeEntry
from .forms import IssueForm, ProjectForm
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.http import JsonResponse
import json
from guardian.mixins import PermissionRequiredMixin


class IndexView(LoginRequiredMixin, generic.ListView):
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


class IssueDetailView(PermissionRequiredMixin, generic.DetailView):
    template_name = "tracker/issue_detail.html"
    model = Issue
    permission_required = "view_project"

    def get_permission_object(self):
        return Issue.objects.get(pk=self.kwargs["pk"]).project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = Issue.objects.get(pk=self.kwargs["pk"]).project.pk
        return context


class IssueListView(PermissionRequiredMixin, generic.ListView):
    template_name = "tracker/issue_list.html"
    model = Issue
    paginate_by = 3
    permission_required = "view_project"

    def get_queryset(self):
        self.project = get_object_or_404(Project, pk=self.kwargs["pk"])
        return Issue.objects.filter(project=self.project)

    def get_permission_object(self):
        return get_object_or_404(Project, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = self.project
        context["project_pk"] = self.kwargs["pk"]

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user_pk"] = self.request.user.pk
        return kwargs

    def form_valid(self, form):
        issue = form.save(commit=False)
        issue.creator = self.request.user
        return super().form_valid(form)


class IssueUpdateView(PermissionRequiredMixin, generic.UpdateView):
    template_name = "tracker/issue_form.html"
    form_class = IssueForm
    model = Issue
    permission_required = "change_project_issue"

    def get_permission_object(self):
        issue = get_object_or_404(Issue, pk=self.kwargs["pk"])
        return issue.project

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user_pk"] = self.request.user.pk
        return kwargs

    def form_valid(self, form):
        issue = form.save(commit=False)
        issue.last_update_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = Issue.objects.get(pk=self.kwargs["pk"]).project.pk
        return context


class IssueDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Issue
    permission_required = "delete_issue"

    def delete(self, request, *args, **kwargs):
        # Extending 'delete' method to update 'last_update_by' field
        # which will be used in 'post_delete' signal during
        # the creation of deletion log
        pk = self.kwargs["pk"]
        issue = Issue.objects.get(pk=pk)
        issue.last_update_by = self.request.user
        issue.save()
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        project = Issue.objects.get(pk=self.kwargs["pk"]).project
        return project.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = Issue.objects.get(pk=self.kwargs["pk"]).project.pk
        return context


class ProjectListView(LoginRequiredMixin, generic.ListView):
    template_name = "tracker/project_list.html"
    model = Project

    def get_queryset(self):
        return Project.objects.filter(creator=self.request.user)


class ProjectDetailView(PermissionRequiredMixin, generic.DetailView):
    template_name = "tracker/project_detail.html"
    model = Project
    permission_required = "view_project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["pk"]
        return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "tracker/project_form.html"
    form_class = ProjectForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user_pk"] = self.request.user.pk
        return kwargs

    def form_valid(self, form):
        project = form.save(commit=False)
        project.creator = self.request.user
        return super().form_valid(form)


class ProjectUpdateView(PermissionRequiredMixin, generic.UpdateView):
    template_name = "tracker/project_form.html"
    form_class = ProjectForm
    model = Project
    permission_required = "change_project"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user_pk"] = self.request.user.pk
        return kwargs

    def form_valid(self, form):
        project = form.save(commit=False)
        project.last_update_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["pk"]
        return context


class ProjectDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Project
    success_url = reverse_lazy("tracker:project_list")
    permission_required = "delete_project"

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        project = Project.objects.get(pk=pk)
        project.last_update_by = self.request.user
        project.save()
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["pk"]
        return context


@login_required
@require_http_methods(["POST"])
def time_tracker(request, pk):
    issue = Issue.objects.get(pk=pk)
    if not issue:
        return JsonResponse({"message": "There is no issue with this ID."}, status=404)
    data = json.loads(request.body)
    action = data["action"]

    if action.lower() == "start":
        if request.user.profile.has_running_timer:
            return JsonResponse(
                {"message": "You cannot have multiple running time trackers."},
                status=403,
            )
        TimeEntry.objects.create(user=request.user, issue=issue)
        return JsonResponse(
            {"work_effort_actual": issue.work_effort_actual}, status=200
        )

    if action.lower() != "stop":
        return JsonResponse(
            {"work_effort_actual": "Requested action is not recognized."}, status=400
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
    if request.user.profile.has_running_timer:
        time_entry = request.user.time_entries.get(user=request.user, end_time=None)
        return JsonResponse({"work_effort": time_entry.work_effort}, status=200)
    else:
        return JsonResponse(
            {"message": "Current user does not have a running timer."}, status=200
        )


# def time_tracker(request, pk):
#     issue = get_object_or_404(Issue, pk=pk)
#     data = json.loads(request.body)
#     action = data["action"]

#     if action.lower() == "start":
#         if request.user.profile.has_running_timer:
#             raise PermissionDenied("You cannot have multiple running time trackers.")
#         TimeEntry.objects.create(user=request.user, issue=issue)
#         return JsonResponse({"message": "Timer has successfully started."}, status=201)

#     if action.lower() == "stop":
#         time_entry = get_object_or_404(
#             request.user.time_entries,
#             user=request.user,
#             issue=issue,
#             end_time=None,
#         )
#         time_entry.end_time = timezone.now()
#         time_entry.save()
#         return JsonResponse({"message": "Timer has successfully stopped."}, status=200)

#     else:
#         return BadRequest("Requested action is not recognized.")
