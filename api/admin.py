from django.contrib import admin
from .models import OTP, LikedBy, UserProfilePhoto , VideoData , EmailVerificationStatus,History,Bookmark,LoginStatus,ChatRoom,Messages

# Register your models here.

admin.site.register({UserProfilePhoto,VideoData,OTP,EmailVerificationStatus,History,Bookmark,LoginStatus,ChatRoom,Messages,LikedBy})
