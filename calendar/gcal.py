import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from task import Task

CALENDAR_ID = os.environ["CALENDAR_ID"]
SA_JSON_KEYFILE = os.environ["SA_JSON_KEYFILE"]


class Gcal:
    def __init__(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SA_JSON_KEYFILE,
            scopes="https://www.googleapis.com/auth/calendar",
        )
        self.api = build("calendar", "v3", credentials=creds)

    def _event_body_from_task(self, task: Task):
        return {
            "summary": task.title,
            "start": {"dateTime": task.scheduled_start, "timeZone": "Europe/Berlin"},
            "end": {"dateTime": task.scheduled_end, "timeZone": "Europe/Berlin"},
            "extendedProperties": {"shared": {"taskapi_id": task.id}},
        }

    def _create_event(self, task):
        self.api.events().insert(
            calendarId=CALENDAR_ID,
            body=self._event_body_from_task(task),
        ).execute()

    def _find_event(self, task_id):
        res = (
            self.api.events()
            .list(
                calendarId=CALENDAR_ID,
                sharedExtendedProperty=f"taskapi_id={task_id}",
            )
            .execute()
        )
        return list(map(lambda x: x["id"], res["items"]))

    def _update_event(self, event_id, task):
        self.api.events().update(
            calendarId=CALENDAR_ID,
            eventId=event_id,
            body=self._event_body_from_task(task),
        ).execute()

    def _delete_event(self, event_id):
        self.api.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()

    def upsert_task(self, task: Task):
        event_ids = self._find_event(task.id)

        if len(event_ids):
            for id in event_ids:
                self._update_event(id, task)
        else:
            self._create_event(task)

    def delete_task(self, task: Task):
        event_ids = self._find_event(task.id)
        for id in event_ids:
            self._delete_event(id)
