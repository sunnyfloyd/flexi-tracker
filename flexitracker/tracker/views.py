from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import generic
from .models import Issue
from .forms import IssueForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


class IndexView(generic.TemplateView):
    template_name = 'tracker/base.html'

class IssueDetailView(generic.DetailView):
    template_name = 'tracker/issue_detail.html'
    model = Issue

class IssueListView(generic.ListView):
    template_name = 'tracker/issue_list.html'
    model = Issue
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adding additional pagination related context to the template
        per_page = context['paginator'].per_page
        page_obj = context['page_obj']
        context['showing_first'] = per_page * (page_obj.number - 1) + 1
        context['showing_end'] = context['showing_first'] + len(page_obj) - 1
        return context

# add a login_required decorator through dispatch method
class IssueFormView(generic.FormView):
    template_name = 'tracker/new_issue.html'
    form_class = IssueForm
    success_url = reverse_lazy('tracker:index')

    def form_valid(self, form):
        issue = form.save(commit=False)
        issue.creator = self.request.user
        issue.save()
        return super().form_valid(form)

class IssueUpdateView(generic.UpdateView):
    template_name = 'tracker/new_issue.html'
    form_class = IssueForm
    model = Issue
    success_url = reverse_lazy('tracker:index')

    # def form_valid(self, form):
    #     issue = form.save(commit=False)
    #     issue.creator = self.request.user
    #     issue.save()
    #     return super().form_valid(form)