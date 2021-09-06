from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import generic
from .models import Issue, Project
from .forms import IssueForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(generic.TemplateView):
    template_name = "tracker/base.html"


class IssueDetailView(generic.DetailView):
    template_name = "tracker/issue_detail.html"
    model = Issue


class IssueListView(generic.ListView):
    template_name = "tracker/issue_list.html"
    model = Issue
    paginate_by = 3

    def get_queryset(self):
        project = get_object_or_404(Project, name__iexact=self.kwargs["project"])
        return Issue.objects.filter(project=project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adding projects
        # context['projects'] = Project.objects.all()

        # Adding pagination
        per_page = context["paginator"].per_page
        page_obj = context["page_obj"]
        context["showing_first"] = per_page * (page_obj.number - 1) + 1
        context["showing_end"] = context["showing_first"] + len(page_obj) - 1
        return context


class IssueFormView(LoginRequiredMixin, generic.CreateView):
    template_name = "tracker/new_issue.html"
    form_class = IssueForm

    def form_valid(self, form):
        issue = form.save(commit=False)
        issue.creator = self.request.user
        issue.save()
        return super().form_valid(form)


class IssueUpdateView(generic.UpdateView):
    template_name = "tracker/issue_edit.html"
    form_class = IssueForm
    model = Issue
    # success_url = reverse_lazy("tracker:index")
