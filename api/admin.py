from django.contrib import admin
from .models import OTP, UserProfilePhoto , VideoData , EmailVerificationStatus

# Register your models here.

admin.site.register({UserProfilePhoto,VideoData,OTP,EmailVerificationStatus})
