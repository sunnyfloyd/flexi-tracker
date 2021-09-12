from .models import Project
from django.db.models import Q


def projects(request):
    return {
        "projects": Project.objects.filter(
            Q(members=request.user) | Q(creator=request.user)
        ).distinct()
        if request.user.is_authenticated
        else []
    }
