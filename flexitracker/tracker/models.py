from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from .utils import get_work_effort
from django.utils import timezone
from django.core.validators import MinValueValidator


class Project(models.Model):

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=1500, default="No description provided.")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_projects",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="projects"
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recently_updated_projects",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("creation_date",)
        permissions = [
            ("change_project_issue", "Can edit issues linked to this project")
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # TODO: should be pointing to the detail view of a project instead of
        # issue list - current approach might be confusing
        return reverse("tracker:issue_list", kwargs={"pk": self.pk})

    @property
    def open_issues(self):
        """Count of open issues linked to the project instance."""
        return self.issues.count() - self.closed_issues

    @property
    def closed_issues(self):
        """Count of closed issues linked to the project instance."""
        return self.issues.filter(status="done").count()

    @property
    def work_effort_actual(self):
        """Total work effort spent on issues linked to the project instance."""
        queryset = TimeEntry.objects.filter(
            Q(issue__in=self.issues.all()), ~Q(end_time=None)
        )
        return get_work_effort(queryset)

    @property
    def progress(self):
        """
        Percentage of closed issues to total number of issues linked to the
        specific project.
        """
        closed_issues = self.closed_issues
        return closed_issues / self.issues.count() * 100 if closed_issues else 0

    @property
    def status_class(self):
        """Generate bootstrap class based on current progress."""
        if self.progress == 100:
            return "success"
        if self.progress > 0:
            return "warning"
        return "danger"

    @property
    def status(self):
        """Generate textual status based on current progress."""
        if self.status_class == "success":
            return "completed"
        if self.status_class == "warning":
            return "in progress"
        return "started"


class Issue(models.Model):

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="issues"
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_issues",
    )
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=1500)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_issues",
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
        ("1", "Top"),
        ("2", "High"),
        ("3", "Medium"),
        ("4", "Low"),
    ]
    priority = models.CharField(
        choices=ISSUE_PRIORITY_CHOICES, max_length=20, default="medium"
    )
    ISSUE_STATUS_CHOICES = [
        ("1", "To-do"),
        ("2", "In progress"),
        ("3", "In review"),
        ("4", "Done"),
    ]
    status = models.CharField(
        choices=ISSUE_STATUS_CHOICES, max_length=20, default="to_do"
    )
    work_effort_estimate = models.IntegerField(validators=[MinValueValidator(1)])
    due_date = models.DateTimeField()
    child_tasks = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="parent_tasks"
    )

    class Meta:
        ordering = (
            "status",
            "priority",
            "-creation_date",
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tracker:issue_detail", kwargs={"pk": self.pk})

    @property
    def contributors(self):
        """
        QuerySet of users who performed any change on this issue instance.
        """
        queryset = Issue.objects.get(pk=self.pk).logs.all().values("user")
        users_pk = {obj["user"] for obj in queryset}
        return get_user_model().objects.filter(pk__in=users_pk)

    @property
    def work_effort_actual(self):
        """Total work effort spent on an issue instance."""
        queryset = TimeEntry.objects.filter(Q(issue=self), ~Q(end_time=None))
        return get_work_effort(queryset)


class Log(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="logs"
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
    # This will result in removal of all of the related logs in case of a deletion
    # of an instance of Issue/Project. From the audit trail perspective this is not
    # something that is desired. However, having a scale of this project
    # and perceived end-user's profile in mind, I decided that any project/issue
    # deletions will be carried out conciously and therefore logging deletion
    # action only should be a sufficient risk mitigating measure.
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
        """
        Log object description based on performed action.
        """
        related_object = (
            "issue"
            if self.issue
            else ("project" if self.project else self.removed_object.split(";")[0])
        )
        removed_object = (
            f" '{self.removed_object.split(';')[1]}'" if self.removed_object else ""
        )
        return f"{self.action.capitalize()}d {related_object}{removed_object}."

    @property
    def description_timeline(self):
        """
        Log object description based on performed action dedicated to user's timeline.
        """
        related_object = (
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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="time_entries"
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
        """Current timer status based on TimeEntry object end_time presence."""
        return self.end_time is None

    @property
    def work_effort(self):
        """
        Work effort based on current time for active timer or based on end_time
        for closed time entries.
        """
        return (
            (self.end_time - self.start_time).total_seconds()
            if self.end_time
            else (timezone.now() - self.start_time).total_seconds()
        )
