from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    test_field = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'Profile for user {self.user.username}'

class Issue(models.Model):
    creator = models.ForeignKey("app.Model", verbose_name=_(""), on_delete=models.CASCADE)

    name = models.CharField(max_length=50)

