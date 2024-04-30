"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from firebase import topic
from notification.models import FCMToken

from .admin import admin_site


# TODO: I have no clue how to serve this from a JS file
# TODO: PLS FIND A WAY TO MOVE THIS OUT OF HERE :(
def service_worker(request):
    data = (
        'importScripts("https://www.gstatic.com/firebasejs/9.18.0/firebase-app-compat.js");'
        'importScripts("https://www.gstatic.com/firebasejs/9.18.0/firebase-messaging-compat.js"); '
        "var firebaseConfig = {"
        '        apiKey: "AIzaSyBWBYDF68ic-f8vT18_JWKoIJOXHolp_n4",'
        '        authDomain: "oceanview-9bd7c.firebaseapp.com",'
        '        projectId: "oceanview-9bd7c",'
        '        storageBucket: "oceanview-9bd7c.appspot.com",'
        '        messagingSenderId: "771961665424",'
        '        appId: "1:771961665424:web:cd47c0b171cdc7e0a82515",'
        '        measurementId: "G-7LMV2TM26W"'
        " };"
        "firebase.initializeApp(firebaseConfig);"
        "const messaging=firebase.messaging();"
        "messaging.onBackgroundMessage((payload) => {"
        "   console.log(payload);"
        "   self.clients.matchAll({includeUncontrolled: true})"
        "   .then(function (clients) {"
        "       console.log(clients); "
        "       for (const client of clients) {"
        "           const url = new URL(client.url);"
        "           console.log(url.pathname);"
        "           if (url.pathname === '/admin/') {"
        "               client.postMessage(payload);"
        "           };"
        "       };"
        "   });"
        "}, e => console.log(e));"
    )

    return HttpResponse(data, content_type="text/javascript")


def logout_view(request):
    user = request.user
    logout(request)
    response = redirect("/admin/")
    fcm_token = request.COOKIES.get("fcm_token")
    print(fcm_token)
    FCMToken.objects.filter(
        token=fcm_token, user=user, device_type=FCMToken.DeviceType.WEB
    ).delete()
    response.delete_cookie("fcm_token")
    topic.unsubscribe_from_topic(fcm_tokens=fcm_token, topic="admin")

    return response


urlpatterns = [
    path("firebase-messaging-sw.js", service_worker, name="show_firebase_js"),
    path("", include("user.urls")),
    path("", include("service.urls")),
    path("", include("invoice.urls")),
    path("", include("feedback.urls")),
    path("", include("locker.urls")),
    path("", include("notification.urls")),
    path("logout/", logout_view, name="logout"),
    path("admin/logout/", lambda _: redirect("/logout/", permanent=False)),
    path("admin/", admin_site.urls),
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("accounts/login/", LoginView.as_view(template_name="admin/login.html")),
    path("accounts/logout/", LogoutView.as_view()),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("swagger/download/", SpectacularAPIView.as_view(), name="schema"),
]
