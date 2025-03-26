from pydoc_data.topics import topics
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponse
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

'''rooms=[
    {'id':1,'name':'Lets learn Python',},
    {'id':2,'name':'Lets learn Django',},
    {'id':3,'name':'Lets learn Studbud',},
]'''


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username not found')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    context = {'page': page}
    return render(request, 'base/login_registration.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error has occurred during the registration')

    return render(request, 'base/login_registration.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q) |
                                Q(host__username__icontains=q)
                                )

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter((Q(room__topic__name__icontains=q)))
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count
        , 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


# Create your views here.

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body'),
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants, }
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

def editProfile(request, pk):
    user = User.objects.get(id=pk)
    form = UserChangeForm(request.post,instance=user)
    if form.is_valid():
        form.save()
        return redirect('user', pk=pk)
    return render(request,'base/edit_old.html',{'form':form})
@login_required(login_url='login')
def create_Room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')
        else:
            print(form.errors)

    return render(request, 'base/create-room.html', context={'form': form})


@login_required(login_url='login')
def delete_Room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not authorized')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def update_Room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not authorized')
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'base/room_form.html', context={'form': RoomForm(instance=room)})


@login_required(login_url='login')
def deletemessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not authorized')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})
