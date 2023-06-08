from typing import cast
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    MeSerializer,
    NotionDbListSerializer,
    NotionDbInfoSerializer,
    GTasksTasklistsSerializer,
    SyncConfigSerializer,
    SyncConfigPartialSerializer,
)
from .models import SyncConfig, UserConnection
from rest_framework.generics import GenericAPIView
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.permissions import IsAuthenticated


class TaggedAutoSchema(AutoSchema):
    def get_tags(self, path, method):
        return ["tasks"]


class Me(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeSerializer
    schema = TaggedAutoSchema()
    # this is a workaroung for OpenAPI schema generation
    # by default, the `get` method here is assumed to do a list operation
    # by explicitely setting action to "retrieve", AutoSchema will assume
    # that this view does a retrieve operation
    # action doesn't seem to have any other effects
    action = "retrieve"

    def get(self, request):
        user = request.user
        cons = user.userconnection
        serializer = MeSerializer(
            {
                "id": user.id,
                "email": user.email,
                "notion": cons.notion_name,
                "g_tasks": cons.g_tasks_name,
            }
        )
        return Response(serializer.data)


class AbstractNotionView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def _api(self, user):
        cons = cast(UserConnection, user.userconnection)
        api = cons.notion_api()
        if api is None:
            raise Http404("Notion connection not found")
        return api


class NotionList(AbstractNotionView):
    serializer_class = NotionDbListSerializer
    schema = TaggedAutoSchema()

    def get(self, request):
        api = self._api(request.user)
        dbs = api.getAvailableDbs()
        return Response(NotionDbListSerializer(dbs, many=True).data)


class NotionDetail(AbstractNotionView):
    serializer_class = NotionDbInfoSerializer
    schema = TaggedAutoSchema()

    def get(self, request, db_id):
        api = self._api(request.user)
        db_info = api.getDbInfo(db_id)
        # TODO check db not exists

        return Response(NotionDbInfoSerializer(db_info).data)


class GTasksList(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GTasksTasklistsSerializer
    schema = TaggedAutoSchema()

    def get(self, request):
        user = request.user
        cons = cast(UserConnection, user.userconnection)
        api = cons.g_tasks_api()
        if api is None:
            raise Http404("Google Tasks connection not found")
        lists = api.taskLists()
        return Response(GTasksTasklistsSerializer(lists, many=True).data)


class SyncConfigList(GenericAPIView):
    permission_classes = [IsAuthenticated]
    # TODO `get` is a partial Serializer
    serializer_class = SyncConfigSerializer
    schema = TaggedAutoSchema()

    def get(self, request):
        user = request.user
        confs = user.syncconfig_set.all()
        return Response(SyncConfigPartialSerializer(confs, many=True).data)

    def post(self, request):
        serializer = SyncConfigSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SyncConfigDetail(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SyncConfigSerializer
    schema = TaggedAutoSchema()

    def _get_object(self, user, pk):
        try:
            return cast(SyncConfig, user.syncconfig_set.get(pk=pk))
        except SyncConfig.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        conf = self._get_object(request.user, pk)
        return Response(SyncConfigSerializer(conf).data)

    def delete(self, request, pk):
        conf = self._get_object(request.user, pk)
        conf.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        conf = self._get_object(request.user, pk)
        serializer = SyncConfigSerializer(conf, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)
