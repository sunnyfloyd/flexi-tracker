from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, Issue, Log

@receiver(post_save)
def log_action(sender, instance, created, update_fields, **kwargs):
    if sender.__name__ == 'Project':
        if created:
            ...
            # Log.objects.create(user=)
        else:
            ...
    elif sender.__name__ == 'Issue':
        ...
    else:
        ...
