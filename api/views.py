from collections import OrderedDict
from django.http import HttpResponse

# for serialization
from django.shortcuts import render, redirect
from .serializers import QuickNotesSerializer, VideoDataSerializer, UserProfilePhotoSerializer
from rest_framework.renderers import JSONRenderer

# for DeSerialization
import io
from rest_framework.parsers import JSONParser

# import models
from .models import EmailVerificationStatus, LoginStatus, QuickNotes, ReportedBy, UserProfilePhoto, LikedBy, PhoneNumber
from .models import VideoData
from .models import OTP
from . models import History
from .models import Bookmark

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# for handling duplicate username exception
from django.db import IntegrityError
# does not exist exception
from django.core.exceptions import ObjectDoesNotExist
# for user creation
from django.contrib.auth.models import User
# for csrf verification
from django.views.decorators.csrf import csrf_exempt

# for sending emails
from django.core.mail import send_mail
# for random number generation
import random
import pywhatkit as pwt  # for sending whatsapp messages
import time  # for sending reminder on a specific time
from datetime import datetime

# For Registering a New User


@csrf_exempt  # to avoid csrf forbideen verification error @
def registerUser(request):
    if request.method == "POST":
        # assuming that , this data is already verified
        userName = request.POST.get('username')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        profile_pic = request.FILES['profile_pic']  # profile_picture

       # if user already exists return - "user already exists"
       # else create the account
        try:
            userObject = User.objects.get(email=email)

            responseObject = {
                "status": 404,
                "response": "The Email is already registered ! Please try logging in"
            }
            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')
        except ObjectDoesNotExist:
            try:
                # userObject = User.objects.create_user(username,email,password)
                userObject = User.objects.create_user(
                    userName, email, password)
                userObject.first_name = firstName
                userObject.last_name = lastName

                # saving profile_photo to UserProfilePhoto Table
                profilePhoto = UserProfilePhoto(
                    profile_pic=profile_pic, user=userObject)
                profilePhoto.save()

                # saving phone number to PhoneNumber
                PhoneNumberObj = PhoneNumber(phone=phone, user=userObject)
                PhoneNumberObj.save()

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

                # responseObject = {
                #     "status": 200,
                #     "response": "User Registered Successfully<br><a href=`https://facebook.com`>Verify Email</a>"
                # }
                # IF USER SUCCESSFULLY GETS REGISTERED, HE/SHE IS REDIRECTED TO OTP PAGE
                # json_data = JSONRenderer().render(responseObject)
                # return HttpResponse(json_data, content_type='application/json')
                return redirect("http://localhost:3000/otp")

            except IntegrityError:
                responseObject = {
                    "status": 404,
                    "response": "username :  '"+userName+"'  is already taken. " + "please try another one"
                }
                json_data = JSONRenderer().render(responseObject)
                return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "Error: Post request needed"
    }
    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# For Email-OTP Verification @


@csrf_exempt
def verifyEmail(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        otpFromFrontend = parsed_data.get('otp')
        email = parsed_data.get('email')

        print(otpFromFrontend, email)
        userObject = User.objects.get(email=email)

        try:
            otpFromBackendObj = OTP.objects.get(user=userObject)
            otpFromBackend = otpFromBackendObj.otp

            if(str(otpFromFrontend) == str(otpFromBackend)):
                emailverificationObject = EmailVerificationStatus(
                    is_email_verified=True, user=userObject)
                emailverificationObject.save()
                responseObject = {
                    "status": 200,
                    "response": "Dear "+str(userObject.username)+" your email is verified successfully !"
                }
                json_data = JSONRenderer().render(responseObject)
                return HttpResponse(json_data, content_type='application/json')

            else:
                responseObject = {
                    "status": 404,
                    "response": "Invalid OTP"
                }
                json_data = JSONRenderer().render(responseObject)
                return HttpResponse(json_data, content_type='application/json')
        
        except OTP.DoesNotExist:
            responseObject = {
                "status": 404,
                "response": "Invalid Entry"
            }
            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST request needed"
    }
    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# For Logging User In @


@csrf_exempt  # to avoid csrf forbiden verification error
def loginUser(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        userName = parsed_data.get('username')
        password = parsed_data.get('password')
        emailFromFrontend = parsed_data.get('email')

        # if username doesn't exist, then error msg would be sent
        if not User.objects.filter(username=userName).exists():
            responseObject = {
                "status": 404,
                "response": "The username doesn't exist"
            }
            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

        # Authenticating user
        user = authenticate(request, username=userName, password=password)

        if user is not None:
            # for successfull login
            userObject = User.objects.get(username=user)

            # verifying email
            emailFromBackend = User.objects.get(username=userName).email
            if(emailFromFrontend != emailFromBackend):
                responseObject = {
                    "status": 404,
                    "response": "email not recognized !"
                }
                json_data = JSONRenderer().render(responseObject)
                # returning response
                return HttpResponse(json_data, content_type='application/json')

            # for logging user in
            LoginStatusValue = LoginStatus.objects.get(user=userObject)
            LoginStatusValue.is_loggedin = True
            LoginStatusValue.save()

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

# For User Logout @


@csrf_exempt  # to avoid csrf forbiden verification error
def logoutUser(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        # for logging user out
        LoginStatusObject = LoginStatus.objects.get(user=userObject)
        LoginStatusObject.is_loggedin = False
        LoginStatusObject.save()

        responseObject = {
            "status": 200,
            "response": "Logged out Successfully"
        }
        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST request needed"
    }
    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# To Upload Video Data @


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
        LoginStatusObject = LoginStatus.objects.get(user=userObject)
        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            username = userObject.username
            video_uploader_img = UserProfilePhoto.objects.get(
                user=userObject).profile_pic

            videoDataObject = VideoData(video_title=video_title, video_desc=video_desc, video_keywords=video_keywords, video_file=video_file,
                                        notes_file=notes_file, video_thumbnail=video_thumbnail, username=username, video_uploader_img=video_uploader_img, user=userObject)
            videoDataObject.save()

            responseObject = {
                "status": 200,
                "response": "Video uploaded Successfully"
            }

            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST request needed"
    }
    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# To increment Like Count @


@csrf_exempt  # to avoid csrf forbiden verification error
def likeVideo(request):
    if request.method == "POST":

        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        video_id = parsed_data.get('sno')
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            try:
                LikedByObject = LikedBy.objects.get(
                    user=userObject, video_id=video_id)
                responseObject = {
                    "status": 404,
                    "response": "You've already liked the video"
                }
                LikedByObject.save()

                json_data = JSONRenderer().render(responseObject)
                return HttpResponse(json_data, content_type='application/json')

            except LikedBy.DoesNotExist:
                LikedByObject = LikedBy(user=userObject, video_id=video_id)
                LikedByObject.save()

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
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST Request was expected !"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# To increment View Count @


@csrf_exempt  # to avoid csrf forbiden verification error
def viewVideo(request):
    if request.method == "POST":

        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        video_id = parsed_data.get('sno')
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in

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
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST request was expected"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# To increment Video Report Count @


@csrf_exempt  # to avoid csrf forbiden verification error
def reportVideo(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        video_id = parsed_data.get('sno')
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            try:
                ReportedByObject = ReportedBy.objects.get(
                    user=userObject, video_id=video_id)

                responseObject = {
                    "status": 404,
                    "response": "You've already reported the video"
                }
                ReportedByObject.save()

                json_data = JSONRenderer().render(responseObject)
                return HttpResponse(json_data, content_type='application/json')

            except ReportedBy.DoesNotExist:
                ReportedByObject = ReportedBy(
                    user=userObject, video_id=video_id)
                ReportedByObject.save()

                reportedVideoObject = VideoData.objects.get(sno=video_id)
                reportedVideoObject.video_report_count += 1

                responseObject = {
                    "status": 200,
                    "response": "Video reported Successfully"
                }

                # name is required for warning message string
                ReportedVideoName = VideoData.objects.get(
                    sno=video_id).video_title

                # send warning message if report count is 4
                if(reportedVideoObject.video_report_count == 4):
                    # Getting email from database , for sending security alert for bad credentials !
                    email_mesg = "Warning"+"\n\n"+"Dear "+str(userObject.username) + \
                        ", your video titled '"+str(ReportedVideoName) + "', has been reported by 4 distinct users. Kindly check the authenticity of your content" + \
                        "\n\n"+"Note: According to our guidelines , A video is automatically deleted if reported 10 times"

                    send_mail(
                        'Warning Alert !',
                        email_mesg,
                        'developerus.community@gmail.com',
                        [email],
                        fail_silently=False,
                    )
                reportedVideoObject.save()

                # delete video,  if report count is 10
                if(reportedVideoObject.video_report_count == 10):
                    # Getting email from database , for sending security alert for bad credentials !
                    email_mesg = ""+"\n\n"+"Dear "+str(userObject.username) + \
                        ", your video titled '" + \
                        str(ReportedVideoName) + \
                        "', has been deleted due to 10 reports by distinct users :("

                    send_mail(
                        'Video Deleted by Learnoscope Community',
                        email_mesg,
                        'developerus.community@gmail.com',
                        [email],
                        fail_silently=False,
                    )
                    reportedVideoObject.delete()
                    reportedVideoObject.save()

                json_data = JSONRenderer().render(responseObject)
                return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST Request was expected !"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')

# to add a video to History section @


@csrf_exempt  # to avoid csrf forbiden verification error
def addToHistory(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        video_id = parsed_data.get('sno')
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            HistoryObject = History(video_id=video_id, user=userObject)
            HistoryObject.save()

            message = {
                "response": "added video to history successfully !",
                "status": 200
            }
            json_data = JSONRenderer().render(message)
            return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    message = {
        "response": "POST request needed",
        "status": 404
    }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# to get user history data @


@csrf_exempt  # to avoid csrf forbiden verification error
def getUserHistory(request):
    # only email is required to know user history
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
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

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    message = {
        "response": "POST request needed",
        "status": 404
    }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# to add a video to Bookmark section @


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
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in

            BookmarkObject = Bookmark(video_id=video_id, user=userObject)
            BookmarkObject.save()

            message = {
                "response": "added video to Bookmark successfully !",
                "status": 200
            }
            json_data = JSONRenderer().render(message)
            return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    message = {
        "response": "POST request needed",
        "status": 404
    }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# to get user Bookmark data @


@csrf_exempt  # to avoid csrf forbiden verification error
def getUserBookmark(request):
    # only email is required to know user history
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
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

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    message = {
        "response": "POST request needed",
        "status": 404
    }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# Search Video @


@csrf_exempt  # to avoid csrf forbiden verification error
def searchVideo(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        search_string = parsed_data.get('search_string')
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in

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
                        "status": 200
                    }
                    json_data = JSONRenderer().render(message)
                    return HttpResponse(json_data, content_type='application/json')
                else:
                    serializer = VideoDataSerializer(
                        AllVideoDataObjects, many=True)
                    responseObject = {
                        "status": 200,
                        "response": serializer.data
                    }

                    json_data = JSONRenderer().render(responseObject)

                    # returning the filtered searched json_video_data
                    return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    json_data = JSONRenderer().render({"response": "POST Request Needed"})
    return HttpResponse(json_data, content_type='application/json')

# for deleting a video object @


@csrf_exempt  # to avoid csrf forbiden verification error
def deleteVideo(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        video_id = parsed_data.get('sno')
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in

            videoDataObject = VideoData.objects.get(sno=video_id)
            videoDataObject.delete()

            message = {
                "response": "Video Deleted Successfully",
                "status": 200
            }
            json_data = JSONRenderer().render(message)
            return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }
        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    message = {"response": "POST Request Needed",
               "status": 404
               }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# for checking the current login status of the user


@csrf_exempt  # to avoid csrf forbiden verification error
def loginStatus(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusValue = LoginStatus.objects.get(user=userObject).is_loggedin

        message = {"response": LoginStatusValue,
                   "status": 200
                   }
        json_data = JSONRenderer().render(message)
        return HttpResponse(json_data, content_type='application/json')

    message = {"response": "POST request needed",
               "status": 404
               }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# for getting video feed


@csrf_exempt  # to avoid csrf forbidden verification error
def getVideoFeed(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            VideoDataObjects = VideoData.objects.all()

            serializer = VideoDataSerializer(VideoDataObjects, many=True)

            # for profile photo of a user
            profile_photoObject = UserProfilePhoto.objects.get(user=userObject)
            profile_photo_serializer = UserProfilePhotoSerializer(
                profile_photoObject)

            # LikedByObj = LikedBy.objects.filter(user=userObject)

# CONTINUE THIS LOGIC
            # LOGIC FOR MERGING PARTICULAR DATA IN SERIALIZED DATA
            # d1=OrderedDict(serializer.data[0])
            # d2=OrderedDict([("like_status",True)])
            # both=OrderedDict(list(d1.items()) + list(d2.items()))
            # print(both);

            responseObject = {
                "status": 200,
                "response": serializer.data,
                "profile_pic": profile_photo_serializer.data
            }

            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }
        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    message = {"response": "POST Request Needed",
               "status": 404
               }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# for getting YOUR VIDEO section data


@csrf_exempt  # to avoid csrf forbidden verification error
def getYourVideos(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            VideoDataObjects = VideoData.objects.filter(user=userObject)
            serializer = VideoDataSerializer(VideoDataObjects, many=True)

            responseObject = {
                "status": 200,
                "response": serializer.data,
            }

            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }
        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    message = {"response": "POST Request Needed",
               "status": 404
               }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')

# FOR SAVING QUICK NOTES


@csrf_exempt  # to avoid csrf forbidden verification error
def saveQuickNotes(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')
        notes_value = parsed_data.get('notes_value')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            # saving quick notes
            QuickNotesObj = QuickNotes(
                notes_value=notes_value, user=userObject)
            QuickNotesObj.save()

            responseObject = {
                "status": 200,
                "response": "Notes Saved Successfully"
            }

            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST Request was expected !"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')


# FOR GETTING DESIRED QUICK NOTES
@csrf_exempt  # to avoid csrf forbidden verification error
def getQuickNotes(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            # saving quick notes
            QuickNotesObj = QuickNotes.objects.filter(user=userObject)
            serializer = QuickNotesSerializer(QuickNotesObj, many=True)
            responseObject = {
                "status": 200,
                "response": serializer.data
            }
            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST Request was expected !"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')


# #REMINDER THROUGH WHATSAPP MESSAGE
@csrf_exempt  # to avoid csrf forbidden verification error
def reminder(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')
        video_id = parsed_data.get('sno')
        timeOfReminder = parsed_data.get('timeOfReminder')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            # evaluating current time
            now = datetime.now()
            current_hour = int(now.strftime("%H"))
            current_minutes = int(now.strftime("%M"))
            hrToSend = current_hour
            minToSend = current_minutes

            if(timeOfReminder == "1h"):
                hrToSend = current_hour+1
            elif(timeOfReminder == "2h"):
                hrToSend = current_hour+2
            elif(timeOfReminder == "15m"):
                minToSend = current_minutes+15
                if(minToSend >= 60):
                    minToSend = minToSend-60
                    hrToSend = current_hour+1
            elif(timeOfReminder == "10m"):
                minToSend = current_minutes+10
                if(minToSend >= 60):
                    minToSend = minToSend-60
                    hrToSend = current_hour+1
            elif(timeOfReminder == "5m"):
                minToSend = current_minutes+1
                if(minToSend >= 60):
                    minToSend = minToSend-60
                    hrToSend = current_hour+1
            else:
                responseObject = {
                    "status": 404,
                    "response": "invalid time format"
                }
                json_data = JSONRenderer().render(responseObject)
                return HttpResponse(json_data, content_type='application/json')

            phoneObject = PhoneNumber.objects.get(user=userObject)
            videoDataObject = VideoData.objects.get(sno=video_id)

            ReminderMessage = "Hey "+userObject.username+", It's a reminder to go through the video named : \"" + \
                videoDataObject.video_title+"\"\n\n\n\n❤Team LearnoScope"
            pwt.sendwhatmsg(phoneObject.phone, ReminderMessage,
                            hrToSend, minToSend, 8, True, 5)

            responseObject = {
                "status": 200,
                "response": "reminder sent on whatsapp"
            }
            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    responseObject = {
        "status": 404,
        "response": "POST Request was expected !"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')


@csrf_exempt  # to avoid csrf forbidden verification error
def getUserProfile(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)

        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            uploadCount = len(VideoData.objects.filter(user=userObject))
            videoSeenCount = len(History.objects.filter(user=userObject))
            bookmarkCount = len(Bookmark.objects.filter(user=userObject))

            # for profile photo of a user
            profile_photoObject = UserProfilePhoto.objects.get(user=userObject)
            profile_photo_serializer = UserProfilePhotoSerializer(
                profile_photoObject)

            responseObject = {
                "status": 200,
                "profile_pic": profile_photo_serializer.data,
                "uploadCount": uploadCount,
                "videoSeenCount": videoSeenCount,
                "bookmarkCount": bookmarkCount,
                "dateJoined": userObject.date_joined,
                "firstName": userObject.first_name,
                "lastName": userObject.last_name
            }

            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }
        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    message = {"response": "POST Request Needed",
               "status": 404
               }
    json_data = JSONRenderer().render(message)
    return HttpResponse(json_data, content_type='application/json')
