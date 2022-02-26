from django.db import models
from django.contrib.auth.models import User


# For Managing User Profile Picture
class UserProfilePhoto(models.Model):
    sno = models.AutoField(primary_key=True)
    profile_pic = models.ImageField(null=True,blank=True,upload_to="profilePhotos")
    user = models.ForeignKey(User,on_delete=models.CASCADE) 
   