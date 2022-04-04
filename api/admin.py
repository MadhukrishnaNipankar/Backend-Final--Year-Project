from django.contrib import admin
from .models import OTP, UserProfilePhoto , VideoData , EmailVerificationStatus,History,Bookmark,LoginStatus

# Register your models here.

admin.site.register({UserProfilePhoto,VideoData,OTP,EmailVerificationStatus,History,Bookmark,LoginStatus})
