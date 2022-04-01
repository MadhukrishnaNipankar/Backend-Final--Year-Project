# for httpresponse
from urllib import response
from django.http import HttpResponse

# for serialization
from django.shortcuts import render
from .serializers import VideoDataSerializer
from rest_framework.renderers import JSONRenderer

# for DeSerialization
import io
from rest_framework.parsers import JSONParser

# import models
from .models import EmailVerificationStatus, UserProfilePhoto
from .models import VideoData
from .models import OTP
from . models import History
from .models import Bookmark


from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# for handling duplicate username exception
from django.db import IntegrityError
from django.contrib.auth.models import User  # for user creation
from django.views.decorators.csrf import csrf_exempt  # for csrf verification

# for sending emails
from django.core.mail import send_mail
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
            # userObject = User.objects.create_user(username,email,password)
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

            # sending otp via mail
            otp_mesg = 'Dear '+userName + \
                ', your One Time Password for verifying the email ' + \
                email+', is '+str(otp)

            send_mail(
                'Team LearnoScope - OTP FOR EMAIL VERIFICATION',
                otp_mesg,
                'developerus.community@gmail.com',
                [email],
                fail_silently=False,
            )

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
                # for successfull login
                login(request, user)

                responseObject = {
                    "status": 200,
                    "response": userName+", your login was successfull"
                }

                json_data = JSONRenderer().render(responseObject)

                # returning response
                return HttpResponse(json_data, content_type='application/json')
            else:

                responseObject = {
                    "status": 404,
                    "response": "Login Failed ! Bad Credentials"
                }

                json_data = JSONRenderer().render(responseObject)

                # Getting email from database , for sending security alert for bad credentials !
                userEmail = User.objects.get(username=userName).email

                email_mesg = "Security Alert !"+"\n\n"+"Dear "+userName + \
                    ", someone just tried logging in your account with bad/wrong credentials! We hope that it was you."

                send_mail(
                    'Team LearnoScope - OTP FOR EMAIL VERIFICATION',
                    email_mesg,
                    'developerus.community@gmail.com',
                    [userEmail],
                    fail_silently=False,
                )

                # returning response
                return HttpResponse(json_data, content_type='application/json')

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

        responseObject = {
            "status": 200,
            "response": "Video uploaded Successfully"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST request needed"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# To increment Like Count


@csrf_exempt  # to avoid csrf forbiden verification error
def likeVideo(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        video_id = parsed_data.get('sno')

        likedVideoObject = VideoData.objects.get(sno=video_id)
        likedVideoObject.video_likes += 1
        likedVideoObject.save()

        responseObject = {
            "status": 200,
            "response": "Video Liked Successfully"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST Request was expected !"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# To increment View Count


@csrf_exempt  # to avoid csrf forbiden verification error
def viewVideo(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        video_id = parsed_data.get('sno')

        viewedVideoObject = VideoData.objects.get(sno=video_id)
        viewedVideoObject.video_views += 1
        viewedVideoObject.save()

        responseObject = {
            "status": 200,
            "response": "Video view count increased Successfully"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST request was expected"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# To increment Video Report Count


@csrf_exempt  # to avoid csrf forbiden verification error
def reportVideo(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        video_id = parsed_data.get('sno')

        reportedVideoObject = VideoData.objects.get(sno=video_id)
        reportedVideoObject.video_report_count += 1
        reportedVideoObject.save()

        responseObject = {
            "status": 200,
            "response": "Video reported Successfully"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST Request was expected !"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# to add a video to History section


@csrf_exempt  # to avoid csrf forbiden verification error
def addToHistory(request):
    # an id and email is expected while adding a video to the history
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        video_id = parsed_data.get('sno')
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        HistoryObject = History(video_id=video_id, user=userObject)
        HistoryObject.save()

        message = {
            "response": "added video to history successfully !",
            "status": 200
        }
        json_data = JSONRenderer().render(message)
        return HttpResponse(json_data, content_type='application/json')

    message = {
        "response": "POST request needed",
        "status": 404
    }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# to get user history data


@csrf_exempt  # to avoid csrf forbiden verification error
def getUserHistory(request):
    # only email is required to know user history
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        HistoryObjects = History.objects.filter(user=userObject)

        responseobject = {"status": 200,
                          "response": []
                          }
        for historyItem in HistoryObjects:
            VideoObject = VideoData.objects.get(sno=historyItem.video_id)
            serializer = VideoDataSerializer(VideoObject)
            responseobject["response"].append(serializer.data)

        json_data = JSONRenderer().render(responseobject)
        return HttpResponse(json_data, content_type='application/json')

    message = {
        "response": "POST request needed",
        "status": 404
    }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# to add a video to Bookmark section


@csrf_exempt  # to avoid csrf forbiden verification error
def addToBookmark(request):
    # an id and email is expected while adding a video to the Bookmark
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        video_id = parsed_data.get('sno')
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        BookmarkObject = Bookmark(video_id=video_id, user=userObject)
        BookmarkObject.save()

        message = {
            "response": "added video to Bookmark successfully !",
            "status": 200
        }
        json_data = JSONRenderer().render(message)
        return HttpResponse(json_data, content_type='application/json')

    message = {
        "response": "POST request needed",
        "status": 404
    }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# to get user Bookmark data


@csrf_exempt  # to avoid csrf forbiden verification error
def getUserBookmark(request):
    # only email is required to know user history
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        BookmarkObjects = Bookmark.objects.filter(user=userObject)

        responseobject = {"status": 200,
                          "response": []
                          }
        for bookmarkItem in BookmarkObjects:
            VideoObject = VideoData.objects.get(sno=bookmarkItem.video_id)
            serializer = VideoDataSerializer(VideoObject)
            responseobject["response"].append(serializer.data)

        json_data = JSONRenderer().render(responseobject)
        return HttpResponse(json_data, content_type='application/json')

    message = {
        "response": "POST request needed",
        "status": 404
    }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# THIS WILL BE IMPROVED MORE IN FUTURE


@csrf_exempt  # to avoid csrf forbiden verification error
def searchVideo(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        search_string = parsed_data.get('search_string')

        if len(search_string) > 80:
            return HttpResponse("search query must be less than 80 characters")
        else:
            VideoDataObjectsByTitle = VideoData.objects.filter(
                video_title__icontains=search_string)
            VideoDataObjectsByDesc = VideoData.objects.filter(
                video_desc__icontains=search_string)
            VideoDataObjectsByKeywords = VideoData.objects.filter(
                video_keywords__icontains=search_string)

            AllVideoDataObjects = VideoDataObjectsByTitle.union(
                VideoDataObjectsByDesc, VideoDataObjectsByKeywords)

            if AllVideoDataObjects.count() == 0:
                message = {
                    "response": "No result found",
                    "status": 404
                }
                json_data = JSONRenderer().render(message)
                return HttpResponse(json_data, content_type='application/json')
            else:
                serializer = VideoDataSerializer(
                    AllVideoDataObjects, many=True)
                json_data = JSONRenderer().render(serializer.data)

                # returning the filtered searched json_video_data
                return HttpResponse(json_data, content_type='application/json')

    json_data = JSONRenderer().render({"response": "POST Request Needed"})
    return HttpResponse(json_data, content_type='application/json')
