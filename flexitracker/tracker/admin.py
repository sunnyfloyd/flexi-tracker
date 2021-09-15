from django.contrib import admin
from .models import Issue, Project, Log, TimeEntry

admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Log)
admin.site.register(TimeEntry)
