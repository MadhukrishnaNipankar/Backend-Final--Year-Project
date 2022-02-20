from django.http import HttpResponse
from django.shortcuts import render

#for handling duplicate username exception
from django.db import IntegrityError

# for user creation
from django.contrib.auth.models import User

# for csrf verification
from django.views.decorators.csrf import csrf_exempt

# our api_key = "developer_us,yadnesh,madhukrishna,vedant,amit,kiran"


@csrf_exempt  # to avoid csrf forbideen verification error
def registerUser(request):
    if request.method == "POST":
        #assuming that , this data is already verified
        userName = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')

        try:
            #userObject = User.objects.create_user("username", "email","password")
            userObject = User.objects.create_user(userName, email, password)
            userObject.first_name = firstName
            userObject.last_name = lastName
            userObject.save()
            return HttpResponse("User Registered successfully")

        except IntegrityError :
            return HttpResponse("username :  '"+userName+"'  is already taken. "+ "please try another one")
