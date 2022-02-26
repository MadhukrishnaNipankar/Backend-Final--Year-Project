from django.http import HttpResponse
from .models import UserProfilePhoto  #import models
from django.db import IntegrityError #for handling duplicate username exception
from django.contrib.auth.models import User # for user creation
from django.views.decorators.csrf import csrf_exempt # for csrf verification


@csrf_exempt  # to avoid csrf forbideen verification error
def registerUser(request):
    if request.method == "POST":
        #assuming that , this data is already verified
        userName = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        profile_pic = request.FILES['profile_pic'] #profile_picture

        try:
            #userObject = User.objects.create_user("username", "email","password")
            userObject = User.objects.create_user(userName, email, password)
            userObject.first_name = firstName
            userObject.last_name = lastName
            
            # saving profile_photo to UserProfilePhoto Table
            profilePhoto = UserProfilePhoto(profile_pic=profile_pic,user=userObject)
            profilePhoto.save()

            userObject.save()    

            return HttpResponse("User Registered successfully")

        except IntegrityError :
            return HttpResponse("username :  '"+userName+"'  is already taken. "+ "please try another one")
