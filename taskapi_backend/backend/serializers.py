from rest_framework import serializers
from .models import SyncConfig


class CsrfSerializer(serializers.Serializer):
    csrftoken = serializers.CharField(read_only=True)


class MeSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    notion = serializers.CharField(read_only=True)
    g_tasks = serializers.CharField(read_only=True)


class NotionDbListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)


class NotionDbInfoSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    date_fields = serializers.DictField(
        read_only=True, child=serializers.CharField(read_only=True)
    )
    checkbox_fields = serializers.DictField(
        read_only=True, child=serializers.CharField(read_only=True)
    )


class GTasksTasklistsSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)


class SyncConfigSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = SyncConfig
        fields = (
            "id",
            "user",
            "notion_db",
            "notion_db_date_prop_id",
            "notion_db_done_prop_id",
            "g_tasks_tasklist",
        )


class SyncConfigPartialSerializer(SyncConfigSerializer):
    class Meta:
        model = SyncConfig
        fields = ("id",)
