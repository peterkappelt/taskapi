"""
URL configuration for taskapi_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path
from allauth.account.views import logout
from backend.notion_oauth_provider.views import (
    oauth2_login as notion_login,
    oauth2_callback as notion_callback,
)

urlpatterns = [
    path("backend/", include("backend.urls")),
    path("admin/", admin.site.urls),
    path(
        "accounts/", include("allauth.urls")
    ),  # TODO only include necessary social provider URLs
    path("accounts/logout/", logout, name="account_logout"),
    path("accounts/taskapi_notion/login/", notion_login, name="notion_login"),
    path(
        "accounts/taskapi_notion/login/callback/",
        notion_callback,
        name="notion_callback",
    ),
]
