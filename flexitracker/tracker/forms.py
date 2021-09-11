from django import forms
from .models import Issue, Project


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        exclude = ("creator", "creation_date", "last_update", "work_effort_actual", 'last_update_by')
        widgets = {"due_date": forms.TextInput(attrs={"type": "date"})}

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ('leader', 'last_update', 'last_update_by')
