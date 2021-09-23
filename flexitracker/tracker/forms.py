from django import forms
from .models import Issue, Project
from django.contrib.auth import get_user_model


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

    # TODO: Limiting selection fields in both project and issue forms should be
    # additionally validated via cleaning methods:
    # clean_projects, clean_child_tasks, clean_members

    def __init__(self, *args, **kwargs):
        user_pk = kwargs.get("user_pk", None)
        if user_pk:
            kwargs.pop("user_pk")
            user = get_user_model().objects.get(pk=user_pk)
            projects = (user.projects.all() | user.created_projects.all()).distinct()
            super().__init__(*args, **kwargs)

            # limiting selection to projects that given user is part of
            self.fields["project"] = forms.ModelChoiceField(queryset=projects)

            # limiting selection to issues that are part of user projects
            self.fields["child_tasks"] = forms.ModelMultipleChoiceField(
                queryset=Issue.objects.filter(project__in=projects)
            )
            self.fields["child_tasks"].required = False


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ("creator", "last_update", "last_update_by")

    def __init__(self, *args, **kwargs):
        # removing project creator and AnonymousUser added by
        # django-guardian to the selection field
        user_pk = kwargs.get("user_pk", None)
        if user_pk:
            kwargs.pop("user_pk")
            super().__init__(*args, **kwargs)
            self.fields["members"] = forms.ModelMultipleChoiceField(
                get_user_model().objects.exclude(pk__in=[1, user_pk])
            )
            self.fields["members"].required = False
