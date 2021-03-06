from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Project, Issue, Log
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Group


# Might want to add time entries logging via TimeEntry model


@receiver(post_save, sender=Project)
def set_project_delete_change_perm(instance, created, **kwargs):
    """
    This is a two-step function:
    1. Assigns deletion and change permissions to a project creator
    for newly created project.
    2. Creates authorization group for newly created project. Members
    of this group can view details of this project and related issues,
    and can change any issue assigned to this project.
    """
    if created:
        # deletion and update permissions for project
        assign_perm("delete_project", instance.creator, instance)
        assign_perm("change_project", instance.creator, instance)

        # initializing view and update permissions for related issues
        group = Group.objects.create(name=f"project_{instance.pk}_members")
        instance.creator.groups.add(group)
        assign_perm("view_project", group, instance)
        assign_perm("change_project_issue", group, instance)


@receiver(post_save, sender=Issue)
def set_issue_delete_perm(instance, created, **kwargs):
    """
    Assigns deletion permission to an issue creator and linked project leader
    for newly created issue.
    """
    if created:
        assign_perm("delete_issue", instance.creator, instance)
        # deletion permission for issue is also granted to project leader
        assign_perm("delete_issue", instance.project.creator, instance)


@receiver(m2m_changed, sender=Project.members.through)
def set_project_member_perm(instance, action, model, pk_set, **kwargs):
    """
    Assigns project members to a dedicated project authorization group
    at every change to the member's pool.
    """
    if action == "post_add":
        group = Group.objects.get(name=f"project_{instance.pk}_members")
        for pk in pk_set:
            model.objects.get(pk=pk).groups.add(group)
            # TODO: implement removal of users from the group
            # that are no longer project members


MODELS = (Project, Issue)

# TODO: Django UpdateView does not handle object updates via
# 'update_fields'. If I wanted to log which fields have been updated
# for update actions I would need to compare in-memory field value
# against the one in DB before object saving (form_valid). I could
# use Django Dirty Fields: https://github.com/romgar/django-dirtyfields


@receiver(post_save)
def log_action(instance, created, **kwargs):
    """
    Logs creation or update action on an instance of a project or an issue object.
    """
    if isinstance(instance, MODELS):
        user = instance.creator if created else instance.last_update_by
        action = "create" if created else "update"
        project = instance if isinstance(instance, Project) else instance.project
        issue = instance if isinstance(instance, Issue) else None
        Log.objects.create(user=user, action=action, project=project, issue=issue)


@receiver(post_delete)
def log_deletion(instance, **kwargs):
    """
    Logs deletion action on an instance of a project or an issue object.
    """
    # Checking for 'instance.last_update_by' ensures that issue deletions
    # that cascaded after project removal would not trigger errors nor would
    # they bloat dashboards that display recent actions.
    if isinstance(instance, MODELS) and instance.last_update_by:
        Log.objects.create(
            user=instance.last_update_by,
            action="delete",
            removed_object=f"{type(instance).__name__};{instance.name}".lower(),
        )
