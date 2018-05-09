from django.shortcuts import render
from django.template import loader
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import UserProfile


def view_profile(request, pk=None):
    if pk:
        user = User.objects.get(pk=pk)
    else:
        user = request.user
    context = {'user': user}
    return render(request, 'accounts/profile.html', context)


def edit_profile(request):
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        city = request.POST.get('city')
        website = request.POST.get('website')
        phone = request.POST.get('phone')
        description = request.POST.get('description')
        
        user = User.objects.get(username=request.user.username)
        user_profile = UserProfile.objects.get(user=user)
   
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        user_profile.city = city
        user_profile.website = website
        user_profile.phone = phone
        user_profile.description = description
        if request.FILES:
            avatar = request.FILES['avatar'] 
            user_profile.image = avatar
            handle_uploaded_file(avatar)
        user_profile.save()
            
    return HttpResponseRedirect(reverse('view_profile'))    


def handle_uploaded_file(f):
    """
    Write file uploaded 
    """
    path = "thuoclao/media/profile_image/" + f.name
    file = open(path, 'wb+')
    for chunk in f.chunks():
        file.write(chunk)
    file.close()
