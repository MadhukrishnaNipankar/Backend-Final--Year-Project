# for httpresponse
from django.http import HttpResponse

#for serialization
from django.shortcuts import render
from .serializers import VideoDataSerializer
from rest_framework.renderers import JSONRenderer

#for DeSerialization
import io
from rest_framework.parsers import JSONParser

# import models
from .models import EmailVerificationStatus, UserProfilePhoto
from .models import VideoData
from .models import OTP


from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# for handling duplicate username exception
from django.db import IntegrityError
from django.contrib.auth.models import User  # for user creation
from django.views.decorators.csrf import csrf_exempt  # for csrf verification

# simple mail transfer protocol - for sending emails
import smtplib
# for random number generation
import random


# For Registering a New User
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
            profilePhoto = UserProfilePhoto(
                profile_pic=profile_pic, user=userObject)
            profilePhoto.save()

            # Saving the User Object
            userObject.save()

            # For Sending OTP for Email Verification
            # it will generate random number of length-5
            random_num = random.randint(10000, 99000)
            otp = random_num

            # saving otp to otp Table
            otp_entry = OTP(otp=otp, user=userObject)
            otp_entry.save()

            # sending email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('developerus.community@gmail.com', 'DeveloperTeam')
            server.sendmail("developerus.community@gmail.com", email, "Subject : One Time Password(otp) : " +
                            str(otp)+"\n\n"+"Dear "+userName+", Your OTP for Email Verification is : "+str(otp))

            return HttpResponse("User Registered Successfully")

        except IntegrityError:
            return HttpResponse("username :  '"+userName+"'  is already taken. " + "please try another one")

    return HttpResponse("Error : POST request Needed")


# For Email-OTP Verification
@csrf_exempt
def verifyEmail(request):
    if request.method == "POST":
        otpFromFrontend = request.POST.get('otp')
        email = request.POST.get('email')

        userObject = User.objects.get(email=email)
        otpFromBackend = OTP.objects.get(user=userObject).otp

        if(str(otpFromFrontend) == str(otpFromBackend)):
            emailverificationObject = EmailVerificationStatus(
                is_email_verified=True, user=userObject)
            emailverificationObject.save()
            return HttpResponse("Dear "+str(userObject.username)+" your email is verified successfully !")
        else:
            return HttpResponse("Invalid OTP")

    return HttpResponse("POST request needed")


# For Logging User In
@csrf_exempt  # to avoid csrf forbiden verification error
def loginUser(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            return HttpResponse("you are already logged in")
        else:
            json_data = request.body
            stream = io.BytesIO(json_data)
            parsed_data = JSONParser().parse(stream)
            userName = parsed_data.get('username')
            password = parsed_data.get('password')
            # Authenticating user
            user = authenticate(request, username=userName, password=password)

            if user is not None:
                #for successfull login
                login(request, user)

                #making json video data 
                videoDataObject = VideoData.objects.all()
                serializer = VideoDataSerializer(videoDataObject,many=True)
                json_data = JSONRenderer().render(serializer.data)

                #returning json_video_data
                return HttpResponse(json_data,content_type='application/json')
            else:
                # Getting email from database , for sending security alert for bad credentials !
                userEmail = User.objects.get(username=userName).email
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login('developerus.community@gmail.com',
                             'DeveloperTeam')
                server.sendmail("developerus.community@gmail.com", userEmail, "Subject : Security Alert ! "+"\n\n"+"Dear " +
                                userName+", someone just tried logging in your account with bad/wrong credentials! We hope that it was you.")
                return HttpResponse("Incorrect Credentials")

    return HttpResponse("Error : POST request Needed")

# For User Logout


@csrf_exempt  # to avoid csrf forbiden verification error
def logoutUser(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            logout(request)
            return HttpResponse("Logged out successfully")
        return HttpResponse("you are not logged in")
    return HttpResponse("Error : POST request Needed")

# To Upload Video Data


@csrf_exempt  # to avoid csrf forbiden verification error
def uploadVideo(request):
    if request.method == "POST":
        email = request.POST.get('email')
        video_title = request.POST.get('videoTitle')
        video_desc = request.POST.get('videoDesc')
        video_keywords = request.POST.get('keywords')
        video_file = request.FILES['videoFile']
        notes_file = request.FILES['notesFile']
        video_thumbnail = request.FILES['thumbnail']

        # getting the userObject according to email
        userObject = User.objects.get(email=email)
        videoDataObject = VideoData(video_title=video_title, video_desc=video_desc, video_keywords=video_keywords, video_file=video_file,
                                    notes_file=notes_file, video_thumbnail=video_thumbnail, user=userObject)
        videoDataObject.save()

        return HttpResponse("Video Uploaded Successfully")

    return HttpResponse("Error ! Please try again !")

# To increment Like Count


@csrf_exempt  # to avoid csrf forbiden verification error
def likeVideo(request):
    if request.method == "POST":
        sno = request.POST.get('videoId')
        likedVideoObject = VideoData.objects.get(sno=sno)
        likedVideoObject.video_likes += 1
        likedVideoObject.save()

        return HttpResponse("video Liked Successfully")

    return HttpResponse("Error ! something went wrong :(")

# To increment View Count


@csrf_exempt  # to avoid csrf forbiden verification error
def viewVideo(request):
    if request.method == "POST":
        sno = request.POST.get('videoId')
        viewedVideoObject = VideoData.objects.get(sno=sno)
        viewedVideoObject.video_views += 1
        viewedVideoObject.save()

        return HttpResponse("video view count increased Successfully")

    return HttpResponse("Error ! something went wrong :(")

# To increment Video Report Count


@csrf_exempt  # to avoid csrf forbiden verification error
def reportVideo(request):
    if request.method == "POST":
        sno = request.POST.get('videoId')
        reportedVideoObject = VideoData.objects.get(sno=sno)
        reportedVideoObject.video_report_count += 1
        reportedVideoObject.save()

        return HttpResponse("video Reported Successfully")

    return HttpResponse("Error ! something went wrong :(")


#THIS WORK IS IN PROGRESS.....
@csrf_exempt  # to avoid csrf forbiden verification error
def searchVideo(request):
    if request.method == "POST":
       json_data = request.body
       stream = io.BytesIO(json_data)
       parsed_data = JSONParser().parse(stream)
       search_string = parsed_data.get('search_string')

       VideoDataObjects = VideoData.objects.all().values() #contain all the video data objects in a list format

       VideoSearchResultList = []
       for videoObject in VideoDataObjects:
           if(search_string in videoObject["video_title"] or search_string in videoObject["video_desc"] or search_string in videoObject["video_keywords"]):    
              VideoSearchResultList.append(videoObject)
       
       print(VideoSearchResultList)       
       
    return HttpResponse("searched success")