from typing import cast

from ..integrations.notion import NotionApi
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

    # do a full fetch-compare-update cycle

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
    props = {
        "title": {"title": [{"type": "text", "text": {"content": rec.title}}]},
    }
    if rec.date_start is not None:
        # TODO google tasks returns day-only format
        # check and handle that here
        props[conf.notion_db_date_prop_id] = {
            "date": {"start": rec.date_start.isoformat()}
        }
    if rec.date_end is not None:
        props[conf.notion_db_date_prop_id]["date"]["end"] = rec.date_end.isoformat()
    if done is not None:
        props[conf.notion_db_done_prop_id] = {"checkbox": rec.done}
    api.patchDbItem(rec.notion_id, props)


EventBus.subscribe(EventRecordChanged, notion_change)
