from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth import authenticate,logout
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from eshop import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.utils.crypto import get_random_string
from .models import *
from cart.models import *
from .token import generate_token
from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.cache import cache_control,never_cache

def is_user(user):
    return user.is_user

def signup(request):

    if request.method=="POST":
        username=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        phonenumber=request.POST.get('phonenumber')
        referral_code=request.POST.get('referral_code')
        if User.objects.filter(username=username).exists():
            messages.error(request,"User alredy exist,")
            return render(request,'authentication/signup.html',{'referral_code': referral_code})
        if len(username)>10:
            messages.error(request,"username is too long,")
        if pass1 != pass2:
            messages.error(request,"password didn't match")
        if not username.isalnum():
            messages.error(request,"username must be Alpha-Numeric")
            return render(request,'authentication/signup.html')
        referrer = None
        if referral_code:
            try:
                referrer = User.objects.get(referral__referral_code=referral_code)
            except User.DoesNotExist:
                messages.error(request, 'Referral code is incorrect.')
                return render(request,'authentication/signup.html',{'referral_code': referral_code})
        myuser=User.objects.create_user(username,email,pass1)
        myuser.is_active = False
        myuser.save()
        wallet = Wallet.objects.create(user=myuser)
        phone=PersonalDetails.objects.get(user = myuser)
        phone.phonenumber = phonenumber
        phone.save()
        messages.success(request,"Your Account has been Sucessfully created.we have sent you a confirmation email, Please confirm email in order to avtive your account")
        #welcome 
        if referrer:
            Referral.objects.create(user=myuser, referral_code=generate_referral_code(), referred_by=referrer)
        else:
            Referral.objects.create(user=myuser, referral_code=generate_referral_code(), referred_by=None)
        subject= "welcome to eshop-experience the online shoping"
        message="Hello"+ myuser.username + "!!\n" + "Welcome to e-shop \n Thank you for visiting website\n we have also sent you a confoemation email, please confirm your email adress in order to activate your account \n \n Thank You"
        from_email=settings.EMAIL_HOST_USER
        to_list=[myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)
        #email Adress Confirmation
        current_site = get_current_site(request)
        email_subject="Conform your email @e-shop login"
        message2 = render_to_string('authentication/email_confirmation.html',{
            'name' : myuser.username,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)
        })
        email= EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],

        )
        email.fail_silently =True
        email.send()
        return render(request,"authentication/emailwait.html")
    return render(request,"authentication/signup.html")

#this view for login
@cache_control(no_store=True,no_cache=True,must_revalidate=True)
def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('pass1')
        user = authenticate(username=username, password=password)
        if user is not None:
            otp_store = get_random_string(length=5,allowed_chars='0123456789')
            request.session['otp']=otp_store
            request.session['user_pk']=user.pk
            subject="otp confirmation"
            message = f"Your otp is{otp_store}"
            from_email = settings.EMAIL_HOST_USER
            to_list=[user.email]
            send_mail(subject,from_email,message,to_list,fail_silently=True)
            return render(request,'authentication/otp_login.html')
        else:
            messages.error(request, "Username or password is incorrect.")
            return redirect('signin')
    return render(request,'authentication/login.html')

#otp verify
@cache_control(no_store=True,no_cache=True,must_revalidate=True)
def verifyotp(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        send_otp = request.session.get('otp')
        user_id = request.session.get('user_pk')
        store_otp=request.POST['otp']
        if send_otp == store_otp:
            myuser= User.objects.get(id=user_id)
            login(request,myuser)
            return redirect('home')
        else:
            return redirect('signin')
#this is for genatating token
def activate(request,uid64,token):
    try:
        uid= force_str(urlsafe_base64_decode(uid64))
        myuser=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,'authentication/activation_failed.html')

def logout_view(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('home')

def forgetpassword(request):
    if request.method == 'POST':
        username= request.POST.get('username')
        myuser = User.objects.get(username=username)
        email=myuser.email
        messages.success(request,"Your Account has been Sucessfully created.we have sent you a confirmation email, Please confirm email in order to avtive your account")
        #welcome 
        subject= "welcome to eshop-experience the online shoping"
        message="Hello"+ myuser.username + "!!\n" + "Welcome to e-shop \n Thank you for visiting website\n we have also sent you a confoemation email, please confirm your email adress in order to activate your account \n \n Thank You"
        from_email=settings.EMAIL_HOST_USER
        to_list=[myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)
        #email Adress Confirmation
        current_site = get_current_site(request)
        email_subject="Conform your email @e-shop login"
        message2 = render_to_string('authentication/forget_confirmations.html',{
            'name' : myuser.username,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)
        })
        email= EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently =True
        email.send()
        return render(request,'authentication/forgetpassword.html')
    return render(request,'authentication/forgetpassword.html')

def activate_password(request,uid64,token):
    try:
        uid= force_str(urlsafe_base64_decode(uid64))
        myuser=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None
    if myuser is not None and generate_token.check_token(myuser,token):
        request.session['user_id']= myuser.id
        return redirect('reset_password')
    else:
        return render(request,'authentication/activation_failed.html')

def reset_password(request):
    user = request.session.get('user_id')
    if request.method == 'POST':
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if pass1 == pass2 :
            new_password=pass1
            user = User.objects.get(pk = user )
            user.set_password(new_password)
            user.save()
            user = authenticate(request, username=user.username, password=pass1)
            login(request,user)
            return redirect('home')
        else :
             messages.error(request,"Sorry Password dosnt match!!")
    return render(request,'authentication/resetpassword.html')

        
