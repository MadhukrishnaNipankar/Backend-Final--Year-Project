from django.http import HttpResponse
import io
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User
from .models import LoginStatus
from .models import ChatRoom
from .models import Messages
from api.models import ChatRoom
from rest_framework.renderers import JSONRenderer
from .serializers import MessageSerializer

# for csrf verification
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt  # to avoid csrf forbiden verification error
def GetChatRoom(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')
        roomPass = parsed_data.get('roomPass')
        ChatRoomName = parsed_data.get('roomName')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)
        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            if ChatRoom.objects.filter(roomName=ChatRoomName).exists():
                if(ChatRoom.objects.get(roomName=ChatRoomName).roomPass == roomPass):

                    messages = Messages.objects.filter(room=ChatRoomName)
                    serializer = MessageSerializer(messages, many=True)
                    json_data = JSONRenderer().render(serializer.data)

                    # returning the filtered messages
                    return HttpResponse(json_data, content_type='application/json')

                # if password is wrong
                responseObject = {
                    "status": 404,
                    "response": "Incorrect Credentials !"
                }
                json_data = JSONRenderer().render(responseObject)
                return HttpResponse(json_data, content_type='application/json')

            # if chat room does not exist
            responseObject = {
                "status": 404,
                "response": "There is no chat room named - "+str(ChatRoomName)
            }
            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

        # if login is false
        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    # if request is not post
    responseObject = {
        "status": 404,
        "response": "POST Request was expected !"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')


@csrf_exempt  # to avoid csrf forbiden verification error
def SendMessage(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')
        roomPass = parsed_data.get('roomPass')
        ChatRoomName = parsed_data.get('roomName')
        message_value = parsed_data.get('message_value')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)
        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            if(ChatRoom.objects.get(roomName=ChatRoomName).roomPass == roomPass):
                username = userObject.username
                messageObj = Messages(
                    username=username, room=ChatRoomName, value=message_value)
                messageObj.save()
                responseObject = {
                    "status": 200,
                    "response": "Message Sent Successfully!"
                }
                json_data = JSONRenderer().render(responseObject)
                return HttpResponse(json_data, content_type='application/json')
            
            responseObject = {
                "status": 404,
                "response": "Incorrect Credentials !"
                }

            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json') 
                   
         # if login is false
        responseObject = {
                "status": 404,
                "response": "You're not logged in"
            }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')
           

    # if request is not post
    responseObject = {
        "status": 404,
        "response": "POST Request was expected !"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')


@csrf_exempt  # to avoid csrf forbiden verification error
def makeNewChatRoom(request):
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        parsed_data = JSONParser().parse(stream)
        email = parsed_data.get('email')
        roomPassword = parsed_data.get('roomPass')
        ChatRoomName = parsed_data.get('roomName')

        userObject = User.objects.get(email=email)
        LoginStatusObject = LoginStatus.objects.get(user=userObject)
        if(LoginStatusObject.is_loggedin == True):  # verifying if user is logged in
            if ChatRoom.objects.filter(roomName=ChatRoomName).exists():
                responseObject = {
                    "status": 404,
                    "response": "Name Already Taken ! Please choose another name"
                }
                json_data = JSONRenderer().render(responseObject)
                return HttpResponse(json_data, content_type='application/json')

            # if Chatroom name does not already exist
            ChatRoomObj = ChatRoom(roomName=ChatRoomName,roomPass=roomPassword)
            ChatRoomObj.save()

            responseObject = {
                "status": 200,
                "response": "Chat Room Named - "+str(ChatRoomName)+" Created Successfully !"
            }

            json_data = JSONRenderer().render(responseObject)
            return HttpResponse(json_data, content_type='application/json')

        # if login is false
        responseObject = {
            "status": 404,
            "response": "You're not logged in"
        }

        json_data = JSONRenderer().render(responseObject)
        return HttpResponse(json_data, content_type='application/json')

    # if request is not post
    responseObject = {
        "status": 404,
        "response": "POST Request was expected !"
    }

    json_data = JSONRenderer().render(responseObject)
    return HttpResponse(json_data, content_type='application/json')
