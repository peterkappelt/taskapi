from datetime import datetime
import uuid
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .integrations.notion import NotionApi
from .integrations.google import GoogleTaskapi


class UserConnection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def _has_socialtoken_for_provider(self, provider: str):
        social_account = self.user.socialaccount_set.filter(provider=provider).first()
        if social_account is None:
            return False
        if social_account.socialtoken_set.first() is None:
            return False
        return True

    @property
    def notion_available(self):
        return self._has_socialtoken_for_provider("taskapi_notion")

    @property
    def notion_name(self):
        if not self.notion_available:
            return None
        connection = self.user.socialaccount_set.filter(
            provider="taskapi_notion"
        ).first()
        owner = connection.extra_data.get("owner", {}).get("user", {}).get("name", None)
        workspace = connection.extra_data.get("workspace_name", None)
        return f"{owner} ({workspace})"

    def notion_api(self):
        if not self.notion_available:
            return None
        if not hasattr(self, "_notion_api"):
            token = (
                self.user.socialaccount_set.filter(provider="taskapi_notion")
                .first()
                .socialtoken_set.first()
            )
            self._notion_api = NotionApi(token.token)
        return self._notion_api

    @property
    def g_tasks_available(self):
        # TODO check if the scope of the token actually allows access to tasks
        return self._has_socialtoken_for_provider("google")

    @property
    def g_tasks_name(self):
        if not self.g_tasks_available:
            return None
        connection = self.user.socialaccount_set.filter(provider="google").first()
        return connection.extra_data.get("name", None)

    def g_tasks_api(self):
        if not self.g_tasks_available:
            return None
        if not hasattr(self, "_g_tasks_api"):
            token = (
                self.user.socialaccount_set.filter(provider="google")
                .first()
                .socialtoken_set.first()
            )
            self._g_tasks_api = GoogleTaskapi(token)
        return self._g_tasks_api


@receiver(post_save, sender=User)
def create_user_connections(sender, instance, created, **kwargs):
    if created:
        UserConnection.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_connections(sender, instance, **kwargs):
    instance.userconnection.save()


# class GoogleCon(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     last_access_token = models.TextField()

#     def taskapi(self):
#         return GoogleTaskapi(self.last_access_token)


class SyncConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    notion_db = models.CharField(max_length=36)
    notion_db_date_prop_id = models.CharField(max_length=32)
    notion_db_done_prop_id = models.CharField(max_length=32, null=True)
    notion_last_edit = models.DateTimeField(default=datetime.utcnow)

    g_tasks_tasklist = models.TextField(null=True)
    g_tasks_last_edit = models.DateTimeField(null=True)


class SyncedRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sync_config = models.ForeignKey(SyncConfig, on_delete=models.CASCADE)

    notion_id = models.CharField(max_length=36)

    title = models.CharField(max_length=200)
    date_start = models.DateTimeField(null=True)
    date_end = models.DateTimeField(null=True)
    done = models.BooleanField(null=True)

    g_tasks_id = models.CharField(max_length=64, null=True)
