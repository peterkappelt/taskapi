from django.urls import path

# from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.schemas import get_schema_view

from . import views

urlpatterns = [
    path(
        "schema/",
        get_schema_view(
            title="TaskAPI Backend", description="TaskAPI Backend", version="1.0.0"
        ),
        name="openapi-schema",
    ),
    path("csrf/", views.CsrfToken.as_view()),
    path("me/", views.Me.as_view()),
    path("notion/", views.NotionList.as_view()),
    path("notion/<str:db_id>/", views.NotionDetail.as_view()),
    path("gtasks/", views.GTasksList.as_view()),
    path("syncconf/", views.SyncConfigList.as_view()),
    path("syncconf/<str:pk>/", views.SyncConfigDetail.as_view()),
]

# urlpatterns = format_suffix_patterns(urlpatterns) # conflicts with generateschema, since it generates duplicate operations
