from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import generic
from .models import Issue, Project
from .forms import IssueForm, ProjectForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(generic.TemplateView):
    template_name = "tracker/base.html"


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
        # project = get_object_or_404(Project, name__iexact=self.kwargs["project"])
        self.project = get_object_or_404(Project, pk=self.kwargs["pk"])
        return Issue.objects.filter(project=self.project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # project name
        context["project_name"] = self.project.name

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
        # issue.save()
        return super().form_valid(form)


class IssueUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "tracker/issue_form.html"
    # template_name = "tracker/issue_edit.html"
    form_class = IssueForm
    model = Issue
    # success_url = reverse_lazy("tracker:index")

    def form_valid(self, form):
        issue = form.save(commit=False)
        issue.last_update_by = self.request.user
        # issue.save()
        return super().form_valid(form)


class ProjectListView(LoginRequiredMixin, generic.ListView):
    template_name = "tracker/project_list.html"
    model = Project

    def get_queryset(self):
        return Project.objects.filter(leader=self.request.user)


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "tracker/project_detail.html"
    model = Project

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["project_pk"] = Issue.objects.get(pk=self.kwargs["pk"]).project.pk
    #     return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "tracker/project_form.html"
    form_class = ProjectForm

    def form_valid(self, form):
        project = form.save(commit=False)
        project.leader = self.request.user
        # project.save()
        return super().form_valid(form)


class ProjectEditView(LoginRequiredMixin, generic.UpdateView):
    template_name = "tracker/project_form.html"
    form_class = ProjectForm
    model = Project

    def form_valid(self, form):
        project = form.save(commit=False)
        project.last_update_by = self.request.user
        # project.save()
        return super().form_valid(form)


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    success_url = reverse_lazy("tracker:project_list")
