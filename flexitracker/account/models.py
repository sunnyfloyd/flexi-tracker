from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    test_field = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'Profile for user {self.user.username}'
