from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Tuple
import requests
from dataclasses import dataclass
from django.utils import timezone

NOTION_VERSION = "2022-06-28"
API_BASE = "https://api.notion.com/v1"


@dataclass
class NotionDb:
    id: str
    title: str


@dataclass
class NotionDbInfo:
    _info: object

    def _fields_of_type(self, type: str) -> List[Tuple[str, str]]:
        return [
            (f, v["id"])
            for f, v in self._info["properties"].items()
            if v["type"] == type
        ]

    @property
    def title(self) -> str:
        return " ".join([t["plain_text"] for t in self._info["title"]])

    @property
    def date_fields(self) -> List[Tuple[str, str]]:
        return self._fields_of_type("date")

    @property
    def checkbox_fields(self) -> List[Tuple[str, str]]:
        return self._fields_of_type("checkbox")


@dataclass
class NotionDbRecord:
    # raw notion api info
    _info: object

    @dataclass
    class Field:
        _info: object

        @staticmethod
        def from_api_field(api_field: object) -> NotionDbRecord.Field:
            return NotionDbRecord.Field(api_field)

        @property
        def type(self) -> str:
            return self._info["type"]

        @property
        def date_start(self) -> Optional[datetime]:
            assert self.type == "date"
            if not self._info["date"] or not self._info["date"]["start"]:
                return None
            timestamp = datetime.fromisoformat(self._info["date"]["start"])
            if timestamp.tzinfo is None:
                # notion might return timestamp without timezone (when date only without time is selected)
                # assume server timezone (required for other APIs that expect a full timestamp)
                # TODO take user timezone into account
                timestamp = timestamp.replace(tzinfo=timezone.get_current_timezone())
            return timestamp

        @property
        def date_end(self) -> Optional[datetime]:
            assert self.type == "date"
            if not self._info["date"] or not self._info["date"]["end"]:
                return None
            timestamp = datetime.fromisoformat(self._info["date"]["end"])
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.get_current_timezone())
            return timestamp

        @property
        def done(self) -> bool:
            # this could also be a formula?!
            # assert self.type == "formula" and self._info["formula"]["type"] == "boolean"
            # return self._info["formula"]["boolean"]
            assert self.type == "checkbox"
            return self._info["checkbox"]

        @property
        def title(self) -> str:
            assert self.type == "title"
            return " ".join([t["plain_text"] for t in self._info["title"]])

    @property
    def id(self) -> str:
        return self._info["id"]

    def field(self, field_id: str) -> Optional[NotionDbRecord.Field]:
        rec = next(
            (x for x in self._info["properties"].values() if x["id"] == field_id), None
        )
        return None if rec is None else NotionDbRecord.Field.from_api_field(rec)


@dataclass
class NotionDbRecords:
    items: List[NotionDbRecord]

    @staticmethod
    def from_api_results(api_results: object) -> NotionDbRecords:
        return NotionDbRecords([NotionDbRecord(x) for x in api_results])

    @property
    def latest_edit_time(self) -> Optional[datetime]:
        if len(self.items) == 0:
            return None
        return max(
            [datetime.fromisoformat(x._info["last_edited_time"]) for x in self.items]
        )


class NotionApi:
    def __init__(self, token: str):
        self.token = token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        }

    def getAvailableDbs(self):
        url = f"{API_BASE}/search"
        res = requests.post(
            url,
            headers=self._headers(),
            json={
                "filter": {"value": "database", "property": "object"}
            },  # filter for returning only available dbs
        )
        if res.status_code != 200:
            raise Exception("Notion request failed!")
        results = res.json()["results"]

        def _title(r):
            return " ".join([t["plain_text"] for t in r["title"]])

        return [NotionDb(x["id"], _title(x)) for x in results]

    def getDbInfo(self, db_id: str):
        url = f"{API_BASE}/databases/{db_id}"
        res = requests.get(url, headers=self._headers())
        res.raise_for_status()
        return NotionDbInfo(res.json())

    def getDbItemsModifiedAfter(self, db_id: str, after: datetime):
        url = f"{API_BASE}/databases/{db_id}/query"
        res = requests.post(
            url,
            headers=self._headers(),
            json={
                "filter": {
                    "timestamp": "last_edited_time",
                    "last_edited_time": {"on_or_after": after.isoformat()},
                }
            },
        )
        res.raise_for_status()
        return NotionDbRecords.from_api_results(res.json()["results"])

    def getDbItem(self, item_id: str):
        url = f"{API_BASE}/pages/{item_id}"
        res = requests.get(
            url,
            headers=self._headers(),
        )
        res.raise_for_status()
        return NotionDbRecord(res.json())

    def patchDbItem(self, item_id: str, props: object):
        url = f"{API_BASE}/pages/{item_id}"
        res = requests.patch(
            url,
            headers=self._headers(),
            json={"properties": props},
        )
        res.raise_for_status()
