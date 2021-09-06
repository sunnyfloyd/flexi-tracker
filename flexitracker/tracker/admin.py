from django.contrib import admin
from .models import Issue, Project, Team

admin.site.register(Team)
admin.site.register(Project)
admin.site.register(Issue)
