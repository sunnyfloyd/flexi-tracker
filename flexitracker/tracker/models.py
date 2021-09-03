from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse
from django.contrib.auth import get_user_model

class Issue(models.Model):

    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='created_issues')
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=1500)
    assignee = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='assigned_issues')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    ISSUE_TYPE_CHOICES = [
        ('issue', 'Issue'),
        ('task', 'Task'),
        ('new feature', 'New Feature'),
        ('improvement', 'Improvement'),
    ]
    issue_type = models.CharField(choices=ISSUE_TYPE_CHOICES, max_length=30, default='issue')
    ISSUE_PRIORITY_CHOICES = [
        ('top', 'Top'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    priority = models.CharField(choices=ISSUE_PRIORITY_CHOICES, max_length=20, default='medium')
    work_effort_estimate = models.IntegerField()
    work_effort_actual = models.IntegerField(default=0)
    due_date = models.DateTimeField()
    child_tasks = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='parent_tasks')
    

    class Meta:
        verbose_name = _("Issue")
        verbose_name_plural = _("Issues")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("issue_detail", kwargs={"pk": self.pk})
