from django.db import models
from django.db.models import Q
from django.db.models.fields import CharField
from django.utils.translation import gettext as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from .utils import get_work_effort


class Project(models.Model):

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=1500, default="No description provided.")
    creator = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="created_projects"
    )
    members = models.ManyToManyField(
        get_user_model(), blank=True, related_name="projects"
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    last_update_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="recently_updated_projects",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("-creation_date",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tracker:issue_list", kwargs={"pk": self.pk})

    @property
    def open_issues(self):
        return self.issues.count() - self.closed_issues

    @property
    def closed_issues(self):
        return self.issues.filter(status="done").count()

    @property
    def work_effort_actual(self):
        queryset = TimeEntry.objects.filter(
            Q(issue__in=self.issues.all()), ~Q(end_time=None)
        )
        return get_work_effort(queryset)

    @property
    def progress(self):
        closed_issues = self.closed_issues
        return closed_issues / self.issues.count() * 100 if closed_issues else 0

    @property
    def status(self):
        if self.progress == 100:
            return "success"
        if self.progress > 50:
            return "warning"
        return "danger"


class Issue(models.Model):

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="issues"
    )
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
    last_update_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="recently_updated_issues",
        blank=True,
        null=True,
    )
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
    # work_effort_actual = models.IntegerField(default=0)
    due_date = models.DateTimeField()
    child_tasks = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="parent_tasks"
    )

    class Meta:
        verbose_name = _("Issue")
        verbose_name_plural = _("Issues")
        ordering = ("-creation_date",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tracker:issue_detail", kwargs={"pk": self.pk})

    @property
    def contributors(self):
        queryset = Issue.objects.get(pk=self.pk).logs.all().values("user")
        users_pk = {obj["user"] for obj in queryset}
        return get_user_model().objects.filter(pk__in=users_pk)

    @property
    def work_effort_actual(self):
        queryset = TimeEntry.objects.filter(Q(issue=self), ~Q(end_time=None))
        return get_work_effort(queryset)


class Log(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="logs"
    )
    date = models.DateTimeField(auto_now_add=True)
    LOG_ACTION_CHOICES = [
        ("create", "Created"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]
    action = models.CharField(max_length=50, choices=LOG_ACTION_CHOICES)

    ##############################################################################
    #                                    NOTE                                    #
    ##############################################################################
    # For both foreign keys in the Log model I decided to use 'models.CASCADE'.
    # This will result in removal of all of the related logs. From the audit trail
    # perspective this is not something that is desired. However, having scale of
    # this project and perceived end-user's profile in mind I decided that any
    # project/issue deletions will be concious decisions and therefore logging
    # deletion action only should be sufficient risk mitigating measure.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="logs", blank=True, null=True
    )
    issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, related_name="logs", blank=True, null=True
    )
    removed_object = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        ordering = ("-date",)

    @property
    def description(self):
        related_object = (
            # "issue"
            f"issue"
            if self.issue
            else ("project" if self.project else self.removed_object.split(";")[0])
        )
        removed_object = (
            f" '{self.removed_object.split(';')[1]}'" if self.removed_object else ""
        )
        return f"{self.action.capitalize()}d {related_object}{removed_object}."

    @property
    def description_timeline(self):
        related_object = (
            # "issue"
            f"issue: <a href='{self.issue.get_absolute_url()}'>{self.issue.name}</a>"
            if self.issue
            else (
                f"project: <a href='{self.project.get_absolute_url()}'>{self.project.name}</a>"
                if self.project
                else self.removed_object.split(";")[0]
            )
        )
        removed_object = (
            f" '{self.removed_object.split(';')[1]}'" if self.removed_object else ""
        )
        return f"{self.action.capitalize()}d {related_object}{removed_object}."


class TimeEntry(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="time_entries"
    )
    issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, related_name="time_entries"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("-start_time",)

    @property
    def is_active(self):
        return self.end_time is None

    @property
    def work_effort(self):
        return (self.end_time - self.start_time).total_seconds() if self.end_time else 0
