from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import generic

class IndexView(generic.TemplateView):
    template_name = 'tracker/base.html'
