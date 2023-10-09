from typing import cast

from ..integrations.notion import NotionApi, NotionPageProps
from ..eventbus import EventRecordChanged, EventBus
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def notion_change(e: EventRecordChanged):
    if e.sender == "notion":
        # don't handle events from self to prevent loops
        return
    conf, rec = e.conf, e.record
    api = cast(
        NotionApi | None,
        conf.user.userconnection.notion_api(),
    )  # explicit casting is necessary since userconnection is not typed by django
    assert api is not None

    # if notion_id on the record is not set, it needs to be created
    if rec.notion_id is None:
        item = api.createDbItem(conf.notion_db, NotionPageProps.from_synced_record(rec))
        rec.notion_id = item.id
        rec.save()
        return

    # otherwise, do a full fetch-compare-update cycle

    # get task from notion
    task = api.getDbItem(rec.notion_id)
    title, date = task.field("title").title, task.field(conf.notion_db_date_prop_id)
    done = (
        task.field(conf.notion_db_done_prop_id).done
        if conf.notion_db_done_prop_id is not None
        else None
    )
    assert date is not None  # TODO log error to user if field does not exist

    if (
        rec.date_start == date.date_start
        and rec.date_end == date.date_end
        and title == rec.title
        and ((done is None) or done == rec.done)
    ):
        # record match, no update necessary
        return

    # finally, update record
    api.patchDbItem(rec.notion_id, NotionPageProps.from_synced_record(rec))


EventBus.subscribe(EventRecordChanged, notion_change)
