from django.shortcuts import render, redirect, get_object_or_404
#from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from .models import User, Blogs, UserInfo
from django.contrib import messages
from datetime import timedelta
import datetime
from datetime import datetime as dt
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import Count
import random
from .task import send_email_task
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

# Create your views here.


def signin(request):
    message = {}
    if request.method == "POST":
        uemail = str(request.POST.get("email"))
        passw = str(request.POST.get("password"))

        User = get_user_model()
            
        try:
            user = User.objects.get(email=uemail)
            user_auth = authenticate(username=uemail, password=passw)

            if user_auth is  None:
                messages.error(request, "Password is not correct try again.")
                message = {"message": "Password is not correct try again."}
                return render(request, "sign-in.html", context=message)
            else:
                url = f"/{user.id}/dashboard/"
                User.objects.filter(id=user.id).update(last_login=timezone.now())
                return redirect(url)
            
            
        except User.DoesNotExist:
            messages.error(request, "User Not Exist")
            message = {"message": "User Not Exist"}
            return render(request, "sign-in.html", context=message)

    return render(request, "sign-in.html")


def signup(request):
    message = {}
    if request.method == "POST":
        uemail = str(request.POST.get("email"))
        passw = str(request.POST.get("password"))
        fname = str(request.POST.get("fname"))
        lname = str(request.POST.get("lname"))
        # Create a new user
        try:
            user = User.objects.get(email=uemail)
            messages.error(request, "A user with this email already exists.")
            message = {"message": "A user with this email already exists."}
            return render(request, "sign-up.html", context=message)
        except User.DoesNotExist:
            # Handle the case where the user doesn't exist
            username = lname + "." + fname + "." + uemail.split("@")[0]
            user = User(
                email=uemail,
                first_name=fname,
                last_name=lname,
                date_joined=timezone.now(),
                is_staff=False,
                is_superuser=False,
                is_active=True
            )
            user.set_password(passw)
            user.save()
            userData = User.objects.get(email=uemail)

            userInfo = UserInfo(userName=username.lower(), user_id=userData.id)
            userInfo.save()

            messages.success(
                request,
                f"You have successfully signed up. User Name is {username.lower()} ",
            )
            message = {
                "message": f"You have successfully signed up. User Name is {username.lower()} "
            }
            return render(request, "sign-in.html", context=message)

    return render(request, "sign-up.html")


def dashBoard(request, user_id):
    today = timezone.now().date()
    last_month = timezone.now() - timedelta(days=30)
    last_month_blog_count = Blogs.objects.filter(
        user_id=user_id, createdAt__gte=last_month
    ).count()
    quarter_start_date = datetime.date(today.year, ((today.month - 1) // 3) * 3 + 1, 1)
    quarter_end_date = datetime.date(today.year, ((today.month - 1) // 3) * 3 + 3, 1)
    yesterday = today - timedelta(days=1)
    user_count = User.objects.count()
    user_count_yesterday = User.objects.filter(
        date_joined__gte=yesterday, date_joined__lt=today
    ).count()
    user_count_joined = User.objects.filter(
        date_joined__gte=quarter_start_date, date_joined__lt=quarter_end_date
    ).count()
    increaseUsrFromYest = ((user_count_yesterday) / user_count) * 100
    increaseFromQuater = ((user_count_joined / user_count)) * 100
    users_logged_in_today = User.objects.filter(last_login__date=today).count()
    blog_count = Blogs.objects.filter(user_id=user_id).count()
    start_date = timezone.datetime(today.year, today.month - 2, 1).date()
    end_date = timezone.datetime(today.year, today.month - 1, 1).date() - timedelta(
        days=1
    )
    now = dt.now()
    current_month = now.month

    blog_count_current_month = Blogs.objects.filter(
        createdAt__month=current_month
    ).count()
    blog_count_lasttolastMonth = Blogs.objects.filter(
        createdAt__gte=start_date, createdAt__lte=end_date
    ).count()
    diff_count_blogs = 0
    if last_month_blog_count == 0:
        diff_count_blogs = blog_count_current_month
    else:
        diff_count_blogs = (blog_count_current_month / last_month_blog_count) * 100

    last_9_months = dt.now() - timedelta(days=270)
    blog_count_by_month = (
        Blogs.objects.filter(user_id=user_id, createdAt__gte=last_9_months)
        .annotate(month=TruncMonth("createdAt"))
        .values("month")
        .annotate(count=Count("id"))
    )
    all_months = [dt.now() - timedelta(days=30 * i) for i in range(9)]
    all_months.reverse()

    result = {}

    for month in all_months:
        key = month.strftime("%B %Y")
        result[key] = 0
        for item in blog_count_by_month:
            if item["month"].strftime("%B %Y") == key:
                result[key] = item["count"]
                break

    getBlogs = Blogs.objects.filter().order_by("createdAt").reverse()
    getUserData = User.objects.get(id=user_id)
    data = {
        "userId": user_id,
        "count": user_count,
        "countIncreaseYes": increaseUsrFromYest,
        "joined": user_count_joined,
        "countIncreaseFromQuater": increaseFromQuater,
        "UserLoginToday": users_logged_in_today,
        "blogCount": blog_count,
        "BlogPercentage": diff_count_blogs,
        "graphData": result,
        "getBlogs": getBlogs,
        "userData": getUserData,
    }

    return render(request, "dashboard.html", context=data)


def personalBlogs(request, user_id):
    getUserBlogs = Blogs.objects.filter(user_id=user_id).order_by("createdAt")
    getUserData = User.objects.get(id=user_id)
    data = {"userId": user_id, "UserBlogs": getUserBlogs, "userData": getUserData}

    return render(request, "personalBlogs.html", context=data)


def deleteBlog(request, user_id, id):
    blog = get_object_or_404(Blogs, user_id=user_id, id=id)
    blog.delete()
    return redirect("personalBlogs", user_id=user_id)


def updateBlog(request, user_id, id):
    if request.method == "POST":
        blogName = str(request.POST.get("name"))
        blogDesc = str(request.POST.get("desc"))
        image = request.FILES.get("image")

        blog = Blogs.objects.get(id=id, user_id=user_id)

        if blogName == "":
            blogName = blog.blogName
        if blogDesc == "":
            blogDesc = blog.Description
        if image is None:
            image = blog.img

        blog.blogName = blogName
        blog.Description = blogDesc
        blog.img = image
        blog.updatedAt = timezone.now()
        blog.save()

    return redirect("personalBlogs", user_id=user_id)


def profile(request, user_id):
    user = User.objects.get(id=user_id)
    getBlogCount = Blogs.objects.filter(user_id=user_id).count()
    try:
        userInfo = UserInfo.objects.get(user_id=user_id)
        if userInfo.aboutMe == None:
            userInfo.aboutMe = ""

        if userInfo.address == None:
            userInfo.address = ""

        if userInfo.city == None:
            userInfo.city = ""

        if userInfo.country == None:
            userInfo.country = ""

        if userInfo.postalCode == None:
            userInfo.postalCode = ""
    
    except UserInfo.DoesNotExist:
        
        user_info=UserInfo(user_id=user.id, userName=user.email.split("@")[0])
        user_info.save()
        
        userInfo = UserInfo.objects.get(user_id=user_id)
        if userInfo.aboutMe == None:
            userInfo.aboutMe = ""

        if userInfo.address == None:
            userInfo.address = ""

        if userInfo.city == None:
            userInfo.city = ""

        if userInfo.country == None:
            userInfo.country = ""

        if userInfo.postalCode == None:
            userInfo.postalCode = ""
        
    data = {
        "userId": user_id,
        "userData": user,
        "userInfo": userInfo,
        "blogCount": getBlogCount,
    }

    return render(request, "profile.html", context=data)


def uploadProfileImage(request, user_id):
    if request.method == "POST":
        image = request.FILES.get("image")
        user = User.objects.get(id=user_id)

        if image is None:
            image = user.img

        user.img = image
        user.updatedAt = timezone.now()
        user.save()

    return redirect("profile", user_id=user_id)


def addNewBlog(request, user_id):
    if request.method == "POST":
        blogName = str(request.POST.get("name"))
        blogDesc = str(request.POST.get("desc"))
        image = request.FILES.get("image")

        newBlog = Blogs(
            blogName=blogName,
            Description=blogDesc,
            img=image,
            user_id=user_id,
            createdAt=timezone.now(),
        )
        newBlog.save()

    return redirect("profile", user_id=user_id)


def updateUserInfo(request, user_id):
    if request.method == "POST":
        user = User.objects.get(id=user_id)
        userInfo = UserInfo.objects.get(user_id=user_id)

        uName = str(request.POST.get("uname"))
        fName = str(request.POST.get("fname"))
        lName = str(request.POST.get("lname"))
        address = str(request.POST.get("address"))
        city = str(request.POST.get("city"))
        country = str(request.POST.get("country"))
        about = str(request.POST.get("about"))
        uemail =str(request.POST.get("email"))

        try:
            code = int(request.POST.get("code"))
        except ValueError:
            code = userInfo.postalCode

        if uName == "":
            uName = userInfo.userName
        if fName == "":
            fName = user.first_name
        if lName == "":
            lName = user.last_name
        if city == "":
            city = userInfo.city
        if country == "":
            country = userInfo.country
        if address == "":
            address = userInfo.address
        if str(code) == "":
            code = userInfo.postalCode
        if about == "":
            about = userInfo.aboutMe
        if uemail == "":
            uemail = user.email

        user.first_name = fName
        user.last_name = lName
        userInfo.city = city
        userInfo.country = country
        userInfo.address = address
        userInfo.aboutMe = about
        userInfo.userName = uName
        userInfo.postalCode = code
        user.updatedAt = timezone.now()
        user.email=uemail
        user.save()
        userInfo.save()

    return redirect("profile", user_id=user_id)


def setting(request, user_id):
    user = User.objects.get(id=user_id)
    data = {
        "userId": user_id,
        "userData": user,
    }

    return render(request, "settings.html", context=data)

oPassw = None
nPassw= None
rePassw=None
otp=None

def changePass(request, user_id):

    global oPassw 
    global nPassw
    global rePassw
    global otp

    if request.method == "POST":
        
        nPassw= str(request.POST.get("npassw"))
        
        rePassw= str(request.POST.get("repassw"))
        
        user = User.objects.get(id=user_id)
                 
        otp = random.randint(100000, 1000000)
        verifyOTP(user.email, otp)
    data ={
        "userId":user_id
    }
    return render(request,"verify.html", context=data)

def verifyOTP(email,otp):
    recipient_list=[email]
    yourMail=settings.EMAIL_HOST_USER
    send_email_task.delay("Your Otp to verify",str(otp), yourMail, recipient_list)


def verifyUserOtp(request, user_id):

    global nPassw
    global otp

    if request.method == "POST":
        
        userOtp = str(request.POST.get("otp"))

        user=User.objects.get(id=user_id)
        if str(otp) == userOtp:
            user.set_password(nPassw)
            user.updateAt = timezone.now()
            user.save()

    messages.success(request, 'Password Successfull Changed')
    message="Password Successfull Changed"
    data = {
        'user_id': user_id,
        'message': message,
    }

    return render(request, 'settings.html', data)        
    

