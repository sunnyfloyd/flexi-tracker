from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views import generic
from django.contrib.auth.views import PasswordChangeView
from .models import Profile
from django.urls import reverse_lazy, reverse
from .forms import UserEditForm, ProfileEditForm, UserCreationAccountForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied


class RegistrationFormView(generic.FormView):
    template_name = "account/register.html"
    form_class = UserCreationAccountForm
    success_url = "/account/register_done/"

    def form_valid(self, form):
        new_user = form.save()
        Profile.objects.create(user=new_user)
        return super().form_valid(form)


# Subclassing PasswordChangeView to ensure proper success redirect
class PasswordChangeAccountView(PasswordChangeView):
    success_url = reverse_lazy("account:password_change_done")


def register_done(request):
    return render(request, "account/register_done.html")


def profile_user(request):
    return redirect(request.user.profile.get_absolute_url())


@login_required
def profile(request, pk):
    user = get_user_model().objects.get(pk=pk)
    if request.method == "POST":
        if request.user != user:
            raise PermissionDenied("You cannot edit other user's profile data.")
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse("account:profile", kwargs={"pk": pk}))
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=user.profile)

    return render(
        request,
        "account/profile.html",
        {"user_form": user_form, "profile_form": profile_form, "user": user},
    )
