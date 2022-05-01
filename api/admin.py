from django.contrib import admin
from .models import OTP, LikedBy, UserProfilePhoto , VideoData , EmailVerificationStatus,History,Bookmark,LoginStatus,ChatRoom,Messages,QuickNotes

# Register your models here.

admin.site.register({UserProfilePhoto,VideoData,OTP,EmailVerificationStatus,History,Bookmark,LoginStatus,ChatRoom,Messages,LikedBy,QuickNotes})
