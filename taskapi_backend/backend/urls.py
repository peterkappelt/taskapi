from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path("me/", views.Me.as_view()),
    path("notion/", views.NotionList.as_view()),
    path("notion/<str:db_id>/", views.NotionDetail.as_view()),
    path("gtasks/", views.GTasksList.as_view()),
    path("syncconf/", views.SyncConfigList.as_view()),
    path("syncconf/<str:pk>/", views.SyncConfigDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
