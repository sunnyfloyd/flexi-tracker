from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.views import PasswordChangeView
from .models import Profile
from django.urls import reverse_lazy, reverse
from .forms import UserEditForm, ProfileEditForm, UserCreationAccountForm
from django.contrib.auth.decorators import login_required

# Subclassing PasswordChangeView to ensure proper success redirect
class PasswordChangeAccountView(PasswordChangeView):
    success_url = reverse_lazy('account:password_change_done')

class RegistrationFormView(generic.FormView):
    template_name = 'account/register.html'
    form_class = UserCreationAccountForm
    success_url = '/account/register_done/'

    def form_valid(self, form):
        new_user = form.save()
        Profile.objects.create(user=new_user)
        return super().form_valid(form)

def register_done(request):
    return render(request, 'account/register_done.html')

@login_required
def dashboard(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            instance=request.user,
            data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse('account:dashboard'))
    else:
        user_form = UserEditForm()
        profile_form = ProfileEditForm()
    
    return render(request, 'account/dashboard.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })