
import profile
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Room, Topic, Message, Profile
from .forms import RoomForm, UserForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage, send_mail
from .utils import generate_token
from django.conf import settings
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_activation_email(user: User, request: HttpRequest):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    
    email_body = render_to_string('authentication/activate.html',context={
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.id)),
        'token': generate_token.make_token(user)
    })

    domain = current_site
    print(domain)
    uid = urlsafe_base64_encode(force_bytes(user.id))
    print('uid: '+uid)
    token = generate_token.make_token(user)
    print('token: '+token)

    '''
    send_mail(
        subject=email_subject,
        message=email_body,
        from_email='jeremiahxing@foxmail.com',
        recipient_list=[user.email],
        fail_silently=False
    )
    '''
    email = EmailMessage(subject=email_subject, 
                        body=email_body,
                        from_email='jeremiahxing@foxmail.com',
                        to=[user.email]
                        )
    EmailThread(email).start()



def signUp(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST['Username'].lower()
        try:
            existUser = User.objects.get(username__iexact=username)
            messages.add_message(request, messages.ERROR,
                                'Username already used')
        except:
            password = request.POST['Password']
            last_name = request.POST['LastName'] if request.POST['LastName'] is not None else 'Crooky' 
            first_name = request.POST['FirstName']
            email = request.POST['Email']
            try:
                user = User.objects.create_user(username=username, password=password,email=email,last_name=last_name,first_name=first_name)
                user_profile = Profile.objects.create(user=user)
                user.save()
                user_profile.save()
                send_activation_email(user, request)
                messages.add_message(request, messages.SUCCESS,
                                'We sent you an email to verify your account')
                # login(request, user)
                return redirect(reverse('log-in'))
            except:
                messages.add_message(request, messages.ERROR,
                                'Unknown error happened')
                return HttpResponse('error')
    return render(request, 'user/signUp.html')


def logInPage(request: HttpRequest):
    if request.method == 'POST':
        context = {'data': request.POST}
        username = request.POST['Username'].lower()
        password = request.POST['Password']
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username not exists!')
        user = authenticate(username=username, password=password)
        user_profile = Profile.objects.get(user=user)
        if user and not user_profile.email_is_verified:
            messages.add_message(request, messages.ERROR,
                                'Email is not verified, please check your email inbox')
            return render(request, 'user/logIn.html', context, status=401)

        if not user:
            messages.add_message(request, messages.ERROR,
                                'Invalid credentials, try again')
            return render(request, 'user/logIn.html', context, status=401)

        login(request, user)

        messages.add_message(request, messages.SUCCESS,
                            f'Welcome {user.username}')

        return redirect(reverse('user', kwargs={'userid': user.id}))
    return render(request, 'user/logIn.html')

def logOutUser(request: HttpRequest):
    logout(request)
    return redirect('home')

def activate_user(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = User.objects.get(id=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user_profile = Profile.objects.get(user=user)
        user_profile.email_is_verified = True
        user_profile.save()

        messages.add_message(request, messages.SUCCESS,
                            'Email verified, you can now login')
        return redirect(reverse('log-in'))

    return render(request, 'authentication/activate-failed.html', {"user": user})


def home(request: HttpRequest):
    topics = Topic.objects.alias(rooms=Count('topic2room')).filter(rooms__gt=0).order_by('-rooms')
    context = {'topics': topics}
    return render(request, 'base/home.html', context)

def course(request: HttpRequest):
    t = request.GET.get('t')
    q = request.GET.get('q')
    cond1 = Q(topic__name__icontains=q)
    cond2 = Q(name__icontains=q)
    cond3 = Q(host__username__icontains=q)
    topics = Topic.objects.all().annotate(Count('topic2room')).order_by('-topic2room__count')
    if t is None:
        rooms = Room.objects.all() if q is None else Room.objects.filter(cond1 | cond2 | cond3).distinct()
    else:
        rooms = Room.objects.filter(topic__name__icontains=t)
    room_message = Message.objects.all()
    context = {'topics': topics, 'rooms': rooms, 'room_message': room_message}
    return render(request, 'base/course.html', context)



def user(request: HttpRequest, userid):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    host_rooms = Room.objects.filter(host__id=userid)
    rooms = Room.objects.filter(participants__id=userid)
    form = UserForm(instance=profile)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect(reverse('user', kwargs={'userid': user.id}))
    context = {'user': user, 'hrooms': host_rooms, 'rooms': rooms, 'form': form, 'profile': profile}
    return render(request, 'user/user.html', context)


@login_required
def room(request: HttpRequest, roomid: int):
    room = Room.objects.get(id=roomid)
    messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    context = {'room': room, 'messages': messages, 'participants': participants}
    if request.method == "POST":
        body=request.POST['body']
        if body is not None:
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=body
            )
            room.participants.add(request.user)
            return redirect('room', roomid=room.id)
    return render(request, 'course/room.html', context)

@login_required
def createRoom(request: HttpRequest, userid: int):
    user = User.objects.get(id=userid)
    form = RoomForm()
    if request.method == 'POST':
        roomname = request.POST['name']
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            room = Room.objects.get(name=roomname)
            room.host = user
            room.save()
            return redirect(reverse('user', kwargs={'userid': user.id}))
        else:
            messages.error(request, 'error')
    context = {'form': form, 'user': user} 
    return render(request, 'course/room_form.html', context)

@login_required
def updateRoom(request: HttpRequest, userid: int, roomid: int):
    room = Room.objects.get(id=roomid)
    form = RoomForm(instance=room)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect(reverse('user', kwargs={'userid': userid}))
    context = {'form': form}
    return render(request, 'course/room_form.html', context)

@login_required
def deleteRoom(request: HttpRequest, roomid: int):
    room = Room.objects.get(id=roomid)
    if request.method=='POST':
        room.delete()
        return redirect(reverse('user', kwargs={"userid": request.user.id}))
    context={'obj': room}
    return render(request, 'base/delete.html', context)

@login_required
def deleteMessage(request: HttpRequest, messageid: int):
    message = Message.objects.get(id=messageid)
    if request.method=='POST':
        roomid = message.room.id
        message.delete()
        return redirect(reverse('room', kwargs={"roomid": roomid}))
    context={'obj': message}
    return render(request, 'base/delete.html', context)

def userProfile(request: HttpRequest, userid: str):
    t = request.GET.get('t')
    q = request.GET.get('q')
    cond1 = Q(topic__name__icontains=q)
    cond2 = Q(name__icontains=q)
    cond3 = Q(host__username__icontains=q)

    user = User.objects.get(id=userid)
    if t is None:
        rooms = Room.objects.filter(host=user).distinct() if q is None else Room.objects.filter(host=user).filter(cond1 | cond2 | cond3).distinct()
    else:
        rooms = Room.objects.filter(host=user).filter(topic__name__icontains=t).distinct()
    
    room_message = user.message_set.all()
    topics = Topic.objects.filter(topic2room__host=user).annotate(Count('topic2room')).order_by('-topic2room')
    context = {'user': user, 'rooms': rooms, 'room_message': room_message, 'topics': topics}
    return render(request, 'user/profile.html', context)

@login_required
def leaveRoom(request: HttpRequest, userid: str, roomid: str):
    room = Room.objects.get(id=roomid)
    user = User.objects.get(id=userid)
    ms = Message.objects.filter(Q(user=user)&Q(room=room)).distinct()
    try:
        room.participants.remove(user)
        for m in ms:
            m.delete()
    except:
        pass
    return redirect(reverse('user', kwargs={'userid': userid}))


def editUser(request: HttpRequest, userid: str):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    form = UserForm(instance=profile)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect(reverse('user', kwargs={'userid': user.id}))
    context={'form': form, 'user': user, 'profile': profile}
    return render(request, 'user/edit.html',context)
