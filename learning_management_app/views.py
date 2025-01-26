from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from learning_management_app.EmailBackEnd import EmailBackEnd


# Create your views here.


def showMainPage(request):
    return render(request, "index.html")


def showLoginPage(request):
    return render(request, "login.html")


def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user = EmailBackEnd.authenticate(request,
                                         username=request.POST.get("username"),
                                         password=request.POST.get("password"))
        if user is not None:
            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect("admin_home")
            elif user.user_type == "2":
                return HttpResponseRedirect(reverse("staff_home"))
            elif user.user_type == "3":
                return HttpResponseRedirect(reverse("student_home"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect("/")


def GetUserDetails(request):
    if request.user is not None:
        return HttpResponse("User : " + request.user.email + "usertype : " + request.user.user_type)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")

def showFirebaseJS(request):
    data = 'importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-app.js");' \
           'importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-messaging.js"); ' \
           'var firebaseConfig = {' \
           '        apiKey: "AIzaSyCQ7Eit3cU2z2lVkBTxcYexhkQSWbnJfa8",' \
           '        authDomain: "mokalengitlms-2fd3e.firebaseapp.com",' \
           '        databaseURL: "https://mokalengitlms-2fd3e.firebaseio.com",' \
           '        projectId: "mokalengitlms-2fd3e",' \
           '        storageBucket: "mokalengitlms-2fd3e.appspot.com",' \
           '        messagingSenderId: "186955124438",' \
           '        appId: "1:186955124438:web:8ec8bf1c42a7fb781ac377",' \
           '        measurementId: "G-XY21CKDLX7"' \
           ' };' \
           'firebase.initializeApp(firebaseConfig);' \
           'const messaging=firebase.messaging();' \
           'messaging.setBackgroundMessageHandler(function (payload) {' \
           '    console.log(payload);' \
           '    const notification=JSON.parse(payload);' \
           '    const notificationOption={' \
           '        body:notification.body,' \
           '        icon:notification.icon' \
           '    };' \
           '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
           '});'

    return HttpResponse(data, content_type="text/javascript")
