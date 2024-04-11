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

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import settings
from .admin import admin_site

schema_view = get_schema_view(
    openapi.Info(
        title=f"{settings.COMPANY_NAME} API",
        default_version="v1",
        description=f"APIs for {settings.COMPANY_NAME}",
        contact=openapi.Contact(email="tranlequocthong313@gmail.com"),
        license=openapi.License(name="Trần Lê Quốc Thống"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", include("user.urls")),
    path("admin/", admin_site.urls),
    path("accounts/login/", LoginView.as_view(template_name="admin/login.html")),
    path("accounts/logout/", LogoutView.as_view()),
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
