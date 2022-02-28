from django.http import HttpResponse

 # import models
from .models import UserProfilePhoto 
from .models import VideoData


# for handling duplicate username exception
from django.db import IntegrityError
from django.contrib.auth.models import User  # for user creation
from django.views.decorators.csrf import csrf_exempt  # for csrf verification



@csrf_exempt  # to avoid csrf forbideen verification error
def registerUser(request):
    if request.method == "POST":
        # assuming that , this data is already verified
        userName = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        profile_pic = request.FILES['profile_pic']  # profile_picture

        try:
            #userObject = User.objects.create_user(username,email,password)
            userObject = User.objects.create_user(userName, email, password)
            userObject.first_name = firstName
            userObject.last_name = lastName

            # saving profile_photo to UserProfilePhoto Table
            profilePhoto = UserProfilePhoto(profile_pic=profile_pic, user=userObject)
            profilePhoto.save()
 
            #Saving the User Object
            userObject.save()

            return HttpResponse("User Registered Successfully")

        except IntegrityError:
            return HttpResponse("username :  '"+userName+"'  is already taken. " + "please try another one")


@csrf_exempt  # to avoid csrf forbiden verification error
def uploadVideo(request):
    if request.method == "POST":
        email = request.POST.get('email')
        video_title = request.POST.get('videoTitle')
        video_desc = request.POST.get('videoDesc')
        video_file = request.FILES['videoFile']
        notes_file = request.FILES['notesFile']

        #getting the userObject according to email
        userObject = User.objects.get(email=email)
        videoDataObject = VideoData(video_title=video_title,video_desc=video_desc,video_file=video_file,notes_file=notes_file,user=userObject)    
        videoDataObject.save()

        return HttpResponse("Video Uploaded Successfully")
    
    return HttpResponse("Error ! Please try again !")
