import re
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from . models import *
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='/login')
def home(request):
    return render(request,'home.html')

def logout_user(request):
    logout(request)
    return render(request,'logout.html')

def login_user(request):
    try:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            print(username, password)
            user = User.objects.filter(username=username).first()
            if user is not None:
                profile = Profile.objects.get(user=user)
                if profile.is_verified:
                    user1 = authenticate(username=username, password=password)
                    if user1 is not None:
                        login(request, user1)
                        return redirect('/')
                    else:
                        messages.info(request, 'Invalid Password/Username')
                        return redirect('/login')
                else:
                    messages.info(request, 'Email not verified! Please verify your email')
                    return redirect('/login')
            else:
                messages.info(request, 'This user is not registered!')
                return redirect('/register')
        else:
            return render(request,'login.html')
    except Exception as e:
        print(e)
        messages.info(request, 'Something Went Wrong! Please Try Again after some time')
        return redirect('/login')
    

def register(request):
    try:
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Taken')
                return redirect('/register')
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Used')
                return redirect('/register')
            
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
            auth_token=str(uuid.uuid4())
            profile = Profile.objects.create(user=user, auth_token=auth_token)
            profile.save()
            
            # send verification mail
            send_verification_mail(email, username, auth_token)

            return redirect('/tokensent')
        return render(request,'register.html')
    except Exception as e:
        print(e)
        messages.info(request, 'Something Went Wrong! Please Try Again after some time')
        return redirect('/register')

def send_token(request):
    return render(request,'send_token.html')

def success(request):
    return render(request,'success.html')

def error_page(request):
    return render(request,'error.html')

def verify(request, auth_token):
    try:
        if Profile.objects.filter(auth_token=auth_token).exists():
            if Profile.objects.get(auth_token=auth_token).is_verified:
                messages.info(request, 'Your account is already verified!')
                return redirect('/')
            Profile.objects.filter(auth_token=auth_token).update(is_verified=True)
            return redirect('/success')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        return redirect('/error')




def send_verification_mail(email, username, token):
    subject = 'Django App | Please verify your email address'
    body = "Hey "+str(username)+",\n\n"+"Please click on the link below to verify your email address.\n\n"+"http://127.0.0.1:8000/verify/"+str(token)+"\n\n"+"Thanks,\n"+"Django App"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail( subject, body, email_from, recipient_list )