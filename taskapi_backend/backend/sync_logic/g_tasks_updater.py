from ..eventbus import EventRecordChanged, EventBus
from celery.utils.log import get_task_logger
from ..integrations.google import GoogleTaskapi
from typing import cast

logger = get_task_logger(__name__)


def g_tasks_change(e: EventRecordChanged):
    logger.info(f"{e.sender} changed {e.record}")
    if e.sender == "g_tasks":
        # don't handle events from self to prevent loops
        return
    conf, rec = e.conf, e.record
    if conf.g_tasks_tasklist is None:
        # don't handle events if g_tasks not configured
        return
    api = cast(
        GoogleTaskapi | None,
        conf.user.userconnection.g_tasks_api(),
    )
    assert api is not None

    if rec.g_tasks_id is None:
        # no task created yet
        if rec.date_start is None:
            # ...but it shouldn't be created either
            return
        new_task = api.createTask(
            conf.g_tasks_tasklist, rec.title, rec.date_start, rec.done
        )
        rec.g_tasks_id = new_task.id
        rec.save()
    else:
        # tasks exists, do full fetch-compare-update cycle
        task = api.getTask(conf.g_tasks_tasklist, rec.g_tasks_id)

        # it could be possible that the task was deleted in the meantime
        # however, google only sets the "deleted" flag, so the task is still
        # returned. it will reappear after "patch" is called

        # the date field is now empty. delete the task
        if rec.date_start is None:
            api.deleteTask(conf.g_tasks_tasklist, rec.g_tasks_id)
            rec.g_tasks_id = None
            rec.save()
            return

        # no relevant changes, return
        if (
            task.title == rec.title  # same title
            and task.due.date() == rec.date_start.date()  # same due date
            and (
                rec.done is None or task.done == rec.done
            )  # "done" prop is not handled or same
        ):
            # for due, only date is compared since Google API truncates "due" to date only
            # see: https://developers.google.com/tasks/reference/rest/v1/tasks
            return

        api.patchTask(
            conf.g_tasks_tasklist, rec.g_tasks_id, rec.title, rec.date_start, rec.done
        )


EventBus.subscribe(EventRecordChanged, g_tasks_change)
