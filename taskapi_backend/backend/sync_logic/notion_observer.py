from datetime import timedelta
from typing import List, cast
from uuid import UUID
from celery import group, shared_task
from django.utils import timezone

from ..integrations.notion import NotionApi

from ..models import SyncConfig, SyncedRecord
from ..eventbus import EventBus, EventRecordChanged


@shared_task(name="dispatch_notion_observers")
def dispatch_notion_observers():
    group([run_notion_observer.s(s.id) for s in SyncConfig.objects.all()]).apply_async()


@shared_task(name="run_notion_observer")
def run_notion_observer(sync_config_id: UUID):
    conf = SyncConfig.objects.get(id=sync_config_id)
    api = cast(
        NotionApi | None,
        conf.user.userconnection.notion_api(),
    )  # explicit casting is necessary since userconnection is not typed by django
    assert api is not None

    changes = api.getDbItemsModifiedAfter(conf.notion_db, conf.notion_last_edit)
    if len(changes.items) == 0:
        return None
    if changes.latest_edit_time > conf.notion_last_edit:
        conf.notion_last_edit = changes.latest_edit_time
        conf.save()
    if (timezone.now() - conf.notion_last_edit) > timedelta(minutes=3):
        # there was no edit for the last 3 minutes
        # advance "notion_last_edit" for a minute
        # prevents the last change to be reported over and over again
        conf.notion_last_edit += timedelta(minutes=1)
        conf.save()

    changed_items: List[UUID] = []
    for item in changes.items:
        # check if SyncedRecord exists, create if not
        rec, _ = SyncedRecord.objects.get_or_create(notion_id=item.id, sync_config=conf)

        # TODO notify and abort if the fields do not exist
        # upstream properties in notion
        title = item.field("title").title
        start = item.field(conf.notion_db_date_prop_id).date_start
        end = item.field(conf.notion_db_date_prop_id).date_end
        done = (
            item.field(conf.notion_db_done_prop_id).done
            if conf.notion_db_done_prop_id
            else None
        )

        if (
            rec.title != title
            or rec.date_start != start
            or rec.date_end != end
            or rec.done != done
        ):
            rec.title, rec.date_start, rec.date_end, rec.done = title, start, end, done
            rec.save()
            changed_items.append(rec.id)
            EventBus.publish(EventRecordChanged("notion", conf, rec))

    return changed_items
