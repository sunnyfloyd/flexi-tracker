from django.shortcuts import render, HttpResponse
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class RegistrationForm(generic.FormView):
    template_name = 'account/register.html'
    form_class = UserCreationForm
    success_url = '/account/register_done/'

    def form_valid(self, form):
        new_user = form.save()
        Profile.objects.create(user=new_user)
        return super().form_valid(form)

def register_done(request):
    return render(request, 'account/register_done.html')

def dashboard(request):
    return HttpResponse('All good!')

