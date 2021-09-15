from django.core import exceptions
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.urls import reverse
from django.db.models.functions import TruncDay
from tracker.utils import get_work_effort


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test_field = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Profile for user {self.user.username}"

    def get_absolute_url(self):
        return reverse("account:profile", kwargs={"pk": self.user.pk})

    def get_assigned_issues(self):
        return self.user.assigned_issues.filter(~Q(status="done"))

    @property
    def created_issues_count(self):
        return self.user.created_issues.count()

    @property
    def assigned_issues_count(self):
        return self.get_assigned_issues().count()

    @property
    def logs_grouped_by_day(self):
        logs = self.user.logs.annotate(day=TruncDay("date")).order_by("-date")
        days = sorted(tuple({obj["day"] for obj in logs.values("day")}), reverse=True)
        return {day: logs.filter(day=day) for day in days}

    @property
    def has_running_timer(self):
        try:
            te = self.user.time_entries.get(end_time=None)
        except exceptions.ObjectDoesNotExist:
            return None
        return te.issue.pk

    @property
    def work_effort_actual(self):
        queryset = self.user.time_entries.filter(Q(user=self.user), ~Q(end_time=None))
        return get_work_effort(queryset)
