from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Project, Issue, Log
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Group

MODELS = (Project, Issue)

# should probably add a new function for TimeEntry


@receiver(post_save, sender=Project)
def set_project_delete_permission(instance, created, **kwargs):
    if created:
        # deletion permission
        assign_perm("delete_project", instance.creator, instance)

        # initializing view permission
        group = Group.objects.create(name=f"project_{instance.pk}_members")
        instance.creator.groups.add(group)
        assign_perm("view_project", group, instance)


@receiver(post_save, sender=Issue)
def set_issue_delete_permission(instance, created, **kwargs):
    if created:
        assign_perm("delete_issue", instance.creator, instance)


@receiver(m2m_changed, sender=Project.members.through)
def set_permission_members(instance, action, model, pk_set, **kwargs):
        if action == "post_add":
            group = Group.objects.get(name=f"project_{instance.pk}_members")
            for pk in pk_set:
                model.objects.get(pk=pk).groups.add(group)


# @receiver(post_save, sender=Project)
# def set_project_delete_permission(instance, **kwargs):
#     assign_perm("delete_project", instance.creator, instance)


# @receiver(post_save, sender=Issue)
# def set_issue_delete_permission(instance, **kwargs):
#     assign_perm("delete_issue", instance.creator, instance)


# @receiver(m2m_changed, sender=Project.members.through)
# def set_permission_members(instance, action, model, pk_set, **kwargs):
#     print(action)
#     if action == "post_add":
#         print('I AM HERE')
#         try:
#             group = Group.objects.get(name=f"project_{instance.pk}_members")
#         except ObjectDoesNotExist:
#             print('exception...')
#             group = Group.objects.create(name=f"project_{instance.pk}_members")
#         print(group)
#         print(pk_set)
#         pk_set.add(instance.creator.pk)
#         print(pk_set)
#         print(model)
#         for pk in pk_set:
#             model.objects.get(pk=pk).groups.add(group)
#         assign_perm("view_project", group, instance)


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
        Log.objects.create(user=user, action=action, project=project, issue=issue)


@receiver(post_delete)
def log_deletion(instance, **kwargs):
    if isinstance(instance, MODELS):
        Log.objects.create(
            user=instance.last_update_by,
            action="delete",
            removed_object=f"{type(instance).__name__};{instance.name}".lower(),
        )
