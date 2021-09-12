from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Project, Issue, Log

MODELS = (Project, Issue)

# Django UpdateView does not handle object updates via 'update_fields'.
# If I wanted to log which fields have been updated for update actions
# I would need to compare in-memory field value against the one in DB
# before object saving (form_valid). I could use Django Dirty Fields:
# https://github.com/romgar/django-dirtyfields
@receiver(post_save)
def log_action(instance, created, **kwargs):
    if isinstance(instance, MODELS):
        user = instance.creator if created else instance.last_update_by
        action = "create" if created else "update"
        project = instance if isinstance(instance, Project) else instance.project
        issue = instance if isinstance(instance, Issue) else None
        Log.objects.create(
            user=user, action=action, project=project, issue=issue
        )


@receiver(post_delete)
def log_deletion(instance, **kwargs):
    if isinstance(instance, MODELS):
        Log.objects.create(
            user=instance.last_update_by,
            action="delete",
            removed_object=f"{type(instance).__name__};{instance.name}".lower(),
        )

# @receiver(post_save)
# def log_action(instance, created, **kwargs):
#     if any(isinstance(instance, m) for m in MODELS.values()):
#         action = "new" if created else "update"
#         linked_model = {
#             k: instance for k, v in MODELS.items() if isinstance(instance, v)
#         }

#         # this logic could be removed if uniform naming for user foreignkey
#         # of in-scope models was implemented (to be done in the final project phase)
#         if isinstance(instance, Project):
#             Log.objects.create(user=instance.creator, action=action, **linked_model)
#         elif isinstance(instance, Issue):
#             Log.objects.create(user=instance.creator, action=action, **linked_model)


# @receiver(post_delete)
# def log_deletion(instance, **kwargs):
#     if any(isinstance(instance, m) for m in MODELS.values()):
#         linked_model = {
#             k: instance for k, v in MODELS.items() if isinstance(instance, v)
#         }
#         if isinstance(instance, Project):
#             Log.objects.create(
#                 user=instance.creator, action="delete", removed_object=instance.name
#             )
#         elif isinstance(instance, Issue):
#             Log.objects.create(
#                 user=instance.creator, action="delete", removed_object=instance.name
#             )
