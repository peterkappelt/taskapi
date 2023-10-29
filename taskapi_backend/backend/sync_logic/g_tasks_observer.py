from typing import List, cast
from uuid import UUID
from celery import group, shared_task
from datetime import datetime, timedelta
from celery.utils.log import get_task_logger

from ..integrations.google import GoogleTaskapi
from ..models import SyncConfig, SyncedRecord
from ..eventbus import EventBus, EventRecordChanged

logger = get_task_logger(__name__)

GTASKS_MAGIC_PREFIX = "#t"


@shared_task(name="dispatch_g_tasks_observers")
def dispatch_g_tasks_observers():
    group(
        [
            run_g_tasks_observer.s(s.id)
            for s in SyncConfig.objects.filter(
                g_tasks_tasklist__isnull=False, disabled=False
            )
        ]
    ).apply_async()


@shared_task(name="run_g_tasks_observer")
def run_g_tasks_observer(sync_config_id: UUID):
    conf = SyncConfig.objects.get(id=sync_config_id)
    if conf.g_tasks_last_edit is None:
        # not yet set, set to now
        conf.g_tasks_last_edit = datetime.utcnow()
        conf.save()
    api = cast(
        GoogleTaskapi | None,
        conf.user.userconnection.g_tasks_api(),
    )
    assert api is not None

    changes = api.listTasksUpdatedAfter(conf.g_tasks_tasklist, conf.g_tasks_last_edit)
    if len(changes.items) == 0:
        return None
    if changes.latest_edit_time > conf.g_tasks_last_edit:
        # add a second to the latest edit time
        # google api revents changes on or after the given timestamp
        # prevents last change to be reported multiple times
        # TODO this will create a deadtime window of 1 second
        conf.g_tasks_last_edit = changes.latest_edit_time + timedelta(seconds=1)
        conf.save()

    changed_items: List[UUID] = []
    for item in changes.items:
        if (SyncedRecord.objects.filter(g_tasks_id=item.id).count() == 0) and (
            not item.title.startswith(GTASKS_MAGIC_PREFIX)
        ):
            # skip this item in case it is not synced and
            # does not start with the magic "#t" that indicates
            # that a new task should be created
            continue

        item_title = item.title
        if item_title.startswith(GTASKS_MAGIC_PREFIX):
            # strip the magic prefix
            # this will automatically sync back to gtasks
            item_title = item_title[len(GTASKS_MAGIC_PREFIX) :].lstrip()

        rec, _ = SyncedRecord.objects.get_or_create(
            g_tasks_id=item.id, sync_config=conf
        )

        if (
            rec.title != item_title
            or rec.date_start.date() != item.due.date()
            or (rec.done is not None and rec.done != item.done)
        ):
            rec.title, rec.date_start = item_title, item.due
            if rec.date_end is not None and rec.date_start > rec.date_end:
                # google tasks does not manage end date
                # catch edge case where new date_start would be after date_end
                rec.date_end = None
            if rec.done is not None:
                rec.done = item.done
            rec.save()
            changed_items.append(rec.id)
            EventBus.publish(EventRecordChanged("g_tasks", conf, rec))

    return changed_items
