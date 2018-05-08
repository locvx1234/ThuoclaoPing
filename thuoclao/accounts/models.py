from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    phone = models.IntegerField(default=0)
    image = models.ImageField(upload_to='profile_image', blank=True, default='profile_image/user.png')

    def __str__(self):
        return self.user.username

def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile, sender=User)