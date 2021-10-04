from django import forms
from django.core.exceptions import ValidationError
from .models import Issue, Project
from django.contrib.auth import get_user, get_user_model


class IssueForm(forms.ModelForm):
    assignee = forms.ModelChoiceField(queryset=get_user_model().objects.exclude(pk=1))

    class Meta:
        model = Issue
        exclude = (
            "creator",
            "creation_date",
            "last_update",
            "work_effort_actual",
            "last_update_by",
        )
        widgets = {
            "due_date": forms.TextInput(attrs={"type": "date"}),
            "work_effort_estimate": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        user_pk = kwargs.get("user_pk", None)
        if user_pk:
            kwargs.pop("user_pk")
            user = get_user_model().objects.get(pk=user_pk)
            self.project_scope = (
                user.projects.all() | user.created_projects.all()
            ).distinct()
            self.task_scope = Issue.objects.filter(project__in=self.project_scope)
            super().__init__(*args, **kwargs)

            # limiting selection to projects that given user is part of
            self.fields["project"] = forms.ModelChoiceField(queryset=self.project_scope)

            # limiting selection to issues that are part of user projects
            self.fields["child_tasks"] = forms.ModelMultipleChoiceField(
                queryset=self.task_scope
            )
            self.fields["child_tasks"].required = False

    def clean_project(self):
        cd = self.cleaned_data
        if cd["project"] not in self.project_scope:
            raise ValidationError(
                f"Current user is not allowed to create issues for {cd['project']} project."
            )
        return cd["project"]

    def clean_child_tasks(self):
        cd = self.cleaned_data
        for task in cd["child_tasks"]:
            if task not in self.task_scope:
                raise ValidationError(
                    f"Current user is not allowed to link issues to {task} issue."
                )
        return cd["child_tasks"]


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ("creator", "last_update", "last_update_by")

    def __init__(self, *args, **kwargs):
        # removing from the selection field project creator and AnonymousUser
        # added by django-guardian to the selection field
        user_pk = kwargs.get("user_pk", None)
        if user_pk:
            kwargs.pop("user_pk")
            anonym_pk = get_user_model().objects.get(username="AnonymousUser").pk
            self.user_scope = get_user_model().objects.exclude(
                pk__in=[anonym_pk, user_pk]
            )
            super().__init__(*args, **kwargs)

            self.fields["members"] = forms.ModelMultipleChoiceField(self.user_scope)
            self.fields["members"].required = False

    def clean_members(self):
        cd = self.cleaned_data
        for member in cd["members"]:
            if member not in self.user_scope:
                raise ValidationError(
                    f"Member {member} cannot be assigned to this project."
                )
        return cd["members"]


class SearchForm(forms.Form):
    query = forms.CharField()
