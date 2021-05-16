from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from phone_field import PhoneField

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=300,null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile/',default='../media/profile/1.jpg',null=True,blank=True)

    def __str__(self):
        return self.user.username

    @property
    def profile_image_url(self):
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url


# signals
def save_profile_user(sender, **kwargs):
    if kwargs['created']:
        profile_user = Profile(user=kwargs['instance'])
        profile_user.save()

post_save.connect(save_profile_user, sender=User)
