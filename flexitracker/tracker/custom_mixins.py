from django.views.generic.edit import DeletionMixin, ModelFormMixin
from django.views.generic.base import ContextMixin
from .models import Issue, Project


class ProjectContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.model is Issue:
            context["project_pk"] = Issue.objects.get(pk=self.kwargs["pk"]).project.pk
        elif self.model is Project:
            context["project_pk"] = self.kwargs["pk"]
        return context


class TrackerFormMixin(ModelFormMixin):
    is_update = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user_pk"] = self.request.user.pk
        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        if self.is_update:
            instance.last_update_by = self.request.user
        else:
            instance.creator = self.request.user
        return super().form_valid(form)

# TODO: This probably needs to be moved to pre_delete signal
# to work from Admin Panel, but only if it will not be called
# for cascaded items
class LogDeletionMixin(DeletionMixin):
    def delete(self, request, *args, **kwargs):
        # Extending 'delete' method to update 'last_update_by' field
        # which will be used in 'post_delete' signal during
        # the creation of deletion log
        pk = self.kwargs["pk"]
        instance = self.model.objects.get(pk=pk)
        instance.last_update_by = self.request.user
        instance.save()
        return super().delete(request, *args, **kwargs)
