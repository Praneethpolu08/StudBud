from pydoc_data.topics import topics
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponse
from django.db.models import Q, Count
from .models import Room, Topic, Message,User
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Room, Message




def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Username not found')
            user=None
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    context = {'page': page ,'next': next_url}
    return render(request, 'base/login.html', context)

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()

            user.save()
            login(request, user)
            return redirect('home')
        else:
            if request.POST.get("password1") != request.POST.get("password2"):
                messages.error(request, 'Passwords must match')
            messages.error(request, 'An error has occurred during the registration')

    return render(request, 'base/login.html', {'form': form})

def home(request):
    total_users = User.objects.count()
    q = request.GET.get('q') if request.GET.get('q') else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q)|
                                Q(name__icontains=q) |
                                Q(description__icontains=q) |
                                Q(host__username__icontains=q)
                                )
    Topic.objects.annotate(room_count=Count('room')).filter(room_count=0).delete()
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter((Q(room__topic__name__icontains=q)))
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count
        , 'room_messages': room_messages , 'total_users': total_users}
    return render(request, 'base/home.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    topics= Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html',{'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html',{'room_messages': room_messages})

def feedPage(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q) |
                                Q(host__username__icontains=q)
                                )
    room_count = rooms.count()
    context = {'rooms': rooms, 'room_count': room_count}
    return render(request, 'base/feed.html', context)


@login_required(login_url='login')
def room(request, pk):
    room = get_object_or_404(Room, id=pk)

    # If private room and user not allowed in
    if room.privacy == 'private' and request.user != room.host and request.user not in room.participants.all():
        if request.method == 'POST' and 'room_password' in request.POST:
            password = request.POST.get('room_password')
            if password == room.password:
                room.participants.add(request.user)
                return redirect('room', pk=room.id)  # Refresh view after granting access
            else:
                messages.error(request, 'Invalid password')
                return render(request, 'base/room_password.html', {
                    'room': room,
                    'error': 'Incorrect password'
                })
        else:
            return render(request, 'base/room_password.html', {'room': room})

    # User is allowed in, either by being host, participant, or after password
    if request.method == "POST" and 'body' in request.POST:
        body = request.POST.get('body')
        if body:
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=body,
            )
            room.participants.add(request.user)

            # Optional cleanup logic (can be removed or modified)
            room_messages = room.message_set.all()
            for user in room.participants.all():
                if not room_messages.filter(user=user).exists():
                    room.participants.remove(user)

        return redirect('room', pk=room.id)

    room_messages = room.message_set.all()
    participants = room.participants.all()

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def create_Room(request):
    topics= Topic.objects.all()
    form = RoomForm()
    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        privacy = request.POST.get('privacy')
        password = request.POST.get('password') if privacy == 'private' else None
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            privacy=privacy,
            password=password
        )
        return redirect('home')
    return render(request, 'base/create-room.html', context={'form': form, 'topics': topics})


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
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not authorized')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.privacy = request.POST.get('privacy')
        if room.privacy == 'private':
            room.password = request.POST.get('password')
        room.save()
        return redirect('home')
    return render(request, 'base/create-room.html', context={'form': RoomForm(instance=room),'topics':topics})

@login_required(login_url='login')
def deletemessage(request, pk):
    message = Message.objects.get(id=pk)
    room = message.room
    if request.user != message.user and room.host != request.user:
        return HttpResponse('You are not authorized')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


def exit_participant(request, pk):
    room = Room.objects.get(id=pk)
    print(f"Before: {room.participants.all()}")
    room.participants.remove(request.user)
    print(f"After: {room.participants.all()}")
    return redirect('home')

@login_required(login_url='login')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def edituser(request, pk):
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST,request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user_profile", pk=user.id)
    return render(request,'base/edit-user.html',{'form':form})







