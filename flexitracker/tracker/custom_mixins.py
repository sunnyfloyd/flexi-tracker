from django.views.generic.edit import DeletionMixin, ModelFormMixin
from django.views.generic.base import ContextMixin
from .models import Issue, Project


class ProjectContextMixin(ContextMixin):
    """
    This class is a light wrapper around ContextMixin class to be used with class
    based views.

    It extends a single 'get_context_data' method to enrich passed context with
    an additional 'project_pk' variable which is used to toggle 'active' CSS class
    on a sidebar menu project elements. 'active' class provides visual hint to a user
    to what project given issue is linked to.

    This class applies to views that use Issue model.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.model is Issue:
            context["project_pk"] = Issue.objects.get(pk=self.kwargs["pk"]).project.pk
        elif self.model is Project:
            context["project_pk"] = self.kwargs["pk"]
        return context


class TrackerFormMixin(ModelFormMixin):
    """
    This class is a light wrapper around ModelFormMixin class to be used with class
    based views.

    It extends 'get_form_kwargs' method to pass current user's PK to a linked
    ModelForm.

    It extends 'form_valid' with following flow determined by 'is_update' attribute:

        If view updates linked model object (is_update = True) then after form
        validation 'last_update_by' field gets overwritten with current user object.

        If view creates new object in a model (is_update = False) then object
        is saved with current user as an object creator.

    This class applies to views that use Project or Issue model.
    """

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
# to work from Admin Panel, but it also should not be called
# for cascaded items.
class LogDeletionMixin(DeletionMixin):
    """
    This class is a light wrapper around DeletionMixin class to be used with class
    based views.

    It extends a single 'delete' method by updating 'last_update_by' field of
    a model's object. This field is later used in a 'post_delete' signal receiver
    during the creation of deletion log.

    This class applies to views that use Project or Issue model.
    """

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        instance = self.model.objects.get(pk=pk)
        instance.last_update_by = self.request.user
        instance.save()
        return super().delete(request, *args, **kwargs)
