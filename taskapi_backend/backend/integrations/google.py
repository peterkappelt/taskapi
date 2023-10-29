from __future__ import annotations
from typing import List, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
from dataclasses import dataclass
from allauth.socialaccount.models import SocialToken
import logging

logger = logging.getLogger(__name__)


@dataclass
class GoogleTasklist:
    id: str
    title: str


@dataclass
class GoogleTask:
    _info: object

    @staticmethod
    def from_api_response(api_response: object) -> GoogleTask:
        return GoogleTask(api_response)

    @property
    def id(self):
        return self._info["id"]

    @property
    def title(self):
        return self._info["title"]

    @property
    def due(self):
        return datetime.fromisoformat(self._info["due"])

    @property
    def done(self):
        return self._info["status"] == "completed"

    @property
    def updated(self):
        return datetime.fromisoformat(self._info["updated"])


@dataclass
class GoogleTaskCollection:
    items: List[GoogleTask]

    @staticmethod
    def from_api_response(api_response: object) -> GoogleTaskCollection:
        return GoogleTaskCollection(
            [GoogleTask.from_api_response(task) for task in api_response["items"]]
        )

    @property
    def latest_edit_time(self) -> Optional[datetime]:
        if len(self.items) == 0:
            return None
        return max([x.updated for x in self.items])


class GoogleTaskapi:
    def __init__(self, token: SocialToken):
        def _handle_refresh(request, scopes):
            logger.info(f"Renewing google token for socialaccount {token.account.id}")
            creds = Credentials(
                token=token.token,
                refresh_token=token.token_secret,
                client_id=token.app.client_id,
                client_secret=token.app.secret,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=scopes,
            )
            creds.refresh(request)
            token.token = creds.token
            token.save()
            return creds.token, creds.expiry

        credentials = Credentials(
            token=token.token,
            # Don't provide a refresh token here, but the refresh handler.
            # The refresh handler will refresh (using refresh_token), but
            # also capture the new token and store it for subsequent use
            refresh_handler=_handle_refresh,
            client_id=token.app.client_id,
            client_secret=token.app.secret,
            token_uri="https://oauth2.googleapis.com/token",
        )

        # cache_discovery=False: https://github.com/googleapis/google-api-python-client/issues/299
        # it will print a warning if not explicitely disabled.
        # TODO: do we want some caching here? Seems useless to discover the API every time
        self.api = build("tasks", "v1", credentials=credentials, cache_discovery=False)

    def taskLists(self):
        list = self.api.tasklists().list().execute()
        return [GoogleTasklist(x["id"], x["title"]) for x in list["items"]]

    def createTask(
        self, tasklist_id: str, title: str, due: datetime, done: Optional[bool]
    ):
        # TODO "due" timezones are not handled properly by google
        # for instance: due is 2023-05-29T23:00:00+00:00 and user is in UTC+2
        # task would be due on 2023-05-30T01:00:00+02:00
        # Google just takes the date and ignores the timezone, so due is marked on 29th
        # can be fixed by using user's timezone
        # also required for "patchTask"

        body = {
            "title": title,
            "due": due.isoformat(),
            "status": "completed" if done else "needsAction",
        }
        return GoogleTask(
            self.api.tasks().insert(tasklist=tasklist_id, body=body).execute()
        )

    def getTask(self, tasklist_id: str, task_id: str):
        return GoogleTask(
            self.api.tasks().get(tasklist=tasklist_id, task=task_id).execute()
        )

    def patchTask(
        self,
        tasklist_id: str,
        task_id: str,
        title: str,
        due: datetime,
        done: Optional[bool],
    ):
        body = {
            "id": task_id,
            "title": title,
            "due": due.isoformat(),
            "deleted": False,
            "status": "completed" if done else "needsAction",
        }
        return GoogleTask(
            self.api.tasks()
            .patch(tasklist=tasklist_id, task=task_id, body=body)
            .execute()
        )

    def deleteTask(self, tasklist_id: str, task_id: str):
        return self.api.tasks().delete(tasklist=tasklist_id, task=task_id).execute()

    def listTasksUpdatedAfter(
        self, tasklist_id: str, last_edit: datetime
    ) -> GoogleTaskCollection:
        return GoogleTaskCollection.from_api_response(
            self.api.tasks()
            .list(
                tasklist=tasklist_id,
                updatedMin=last_edit.isoformat(),
                showCompleted=True,
                showHidden=True,
            )
            .execute()
        )
