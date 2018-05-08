from django.shortcuts import render
from django.template import loader
from django.contrib.auth.models import User



def view_profile(request, pk=None):
    if pk:
        user = User.objects.get(pk=pk)
    else:
        user = request.user
    context = {'user': user}
    return render(request, 'accounts/profile.html', context)