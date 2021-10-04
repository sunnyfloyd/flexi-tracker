from .models import Project
from django.db.models import Q


def projects(request):
    """
    If user is authenticated, adds user's projects to each view's context to
    display on a sidebar menu.
    """
    return {
        "projects": Project.objects.filter(
            Q(members=request.user) | Q(creator=request.user)
        ).distinct()
        if request.user.is_authenticated
        else []
    }
