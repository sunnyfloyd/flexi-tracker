from django.db import models
from django.db.models.fields import CharField
from django.utils.translation import gettext as _
from django.urls import reverse
from django.contrib.auth import get_user_model


class Team(models.Model):

    name = CharField(max_length=50)
    leader = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="leading"
    )
    members = models.ManyToManyField(get_user_model(), related_name="teams")

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('team_detail', kwargs={'pk': self.pk})


class Project(models.Model):

    name = models.CharField(max_length=50, unique=True)
    creator = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="created_projects"
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tracker:project_detail', kwargs={'project': self.name})


class Issue(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    creator = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="created_issues"
    )
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=1500)
    assignee = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="assigned_issues"
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    ISSUE_TYPE_CHOICES = [
        ("issue", "Issue"),
        ("task", "Task"),
        ("new feature", "New Feature"),
        ("improvement", "Improvement"),
    ]
    issue_type = models.CharField(
        choices=ISSUE_TYPE_CHOICES, max_length=30, default="issue"
    )
    ISSUE_PRIORITY_CHOICES = [
        ("top", "Top"),
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]
    priority = models.CharField(
        choices=ISSUE_PRIORITY_CHOICES, max_length=20, default="medium"
    )
    ISSUE_STATUS_CHOICES = [
        ("to_do", "To-do"),
        ("in_progress", "In progress"),
        ("in_review", "In review"),
        ("done", "Done"),
    ]
    status = models.CharField(
        choices=ISSUE_STATUS_CHOICES, max_length=20, default="to_do"
    )
    work_effort_estimate = models.IntegerField()
    work_effort_actual = models.IntegerField(default=0)
    due_date = models.DateTimeField()
    child_tasks = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="parent_tasks"
    )

    class Meta:
        verbose_name = _("Issue")
        verbose_name_plural = _("Issues")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tracker:issue_detail", kwargs={"pk": self.pk})
