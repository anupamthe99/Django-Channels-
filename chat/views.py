# chat/views.py
from django.shortcuts import render

from chat.models import Message


def index(request):
    return render(request, "chat/index.html")

def room(request, room_name):
    messages = Message.objects.all()
    return render(request, "chat/room.html", {"room_name": room_name,
                                              'messages':messages})



# def index(request, room_name):
#     messages = Message.objects.all()
#     return render(request, 'chat/index.html', {
#         'room_name_json': mark_safe(json.dumps(room_name)),
#         'messages': messages
#     })