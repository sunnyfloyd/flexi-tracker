from django.contrib import admin
from .models import Issue, Project

admin.site.register(Project)
admin.site.register(Issue)
