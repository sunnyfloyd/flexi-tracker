from django import template
from ..models import Project, Issue

register = template.Library()

# Adding templatetag to toggle 'active' class on a sidebar menu.
# Hardcoded keyword is far from perfect but for now saves redundancy in views.
# @register.simple_tag(takes_context=True)
# def toggle_active(context, pk):
#     print(context['object'])
#     if 'project' in context.request.path:
#         return 'active' if context['project'].pk == pk else ''
#     if 'issue' in context.request.path:
#         return 'active' if Issue.objects.get(pk=context['object'].pk).project.pk == pk else ''
#     return ''
