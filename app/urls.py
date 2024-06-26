from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from firebase.service_worker import service_worker

from .admin import admin_site, logout_view

urlpatterns = [
    path("firebase-messaging-sw.js", service_worker, name="show_firebase_js"),
    path("", include("user.urls")),
    path("", include("service.urls")),
    path("", include("invoice.urls")),
    path("", include("feedback.urls")),
    path("", include("locker.urls")),
    path("", include("notification.urls")),
    path("", include("guide.urls")),
    path("", include("news.urls")),
    path("", include("chat.urls")),
    path("vnpay/", include("vnpay.api_urls")),
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
    path("ckeditor5/", include("django_ckeditor_5.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
