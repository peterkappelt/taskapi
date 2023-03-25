from enum import Enum
from typing import List
from gcal import Gcal
from task import Task, RequiredCommitAction


class ChangeType(Enum):
    New = 0
    Update = 1
    Delete = 2


class State:
    tasks: dict[str, Task] = {}
    cal: Gcal

    def __init__(self):
        self.cal = Gcal()

    def handle_task_change(self, task_change):
        id, change_type = task_change["id"], task_change["type"]

        # check if it is already managed
        existing_task = None
        if id in self.tasks:
            existing_task = self.tasks[id]
            if change_type == ChangeType.Delete.value:
                existing_task.action_gcal = RequiredCommitAction.Delete
                # delete required
                return

            new_task = Task.from_task(task_change["task"])
            if existing_task == new_task:
                # no update required
                return

            # update or delete is required
            self.tasks[id] = new_task
            if new_task.should_be_event():
                new_task.action_gcal = RequiredCommitAction.Upsert
            else:
                new_task.action_gcal = RequiredCommitAction.Delete

        else:
            # not yet managed and delete requested, so return
            if change_type == ChangeType.Delete.value:
                return

            new_task = Task.from_task(task_change["task"])
            if not new_task.should_be_event():
                # only manage tasks that should be event
                return
            new_task.action_gcal = RequiredCommitAction.Upsert
            self.tasks[id] = new_task

    def commit(self):
        # list of tasks to be purged from state after handling
        tasks_to_be_deleted: List[str] = []

        for task in self.tasks.values():
            # handle requested calendar action
            if task.action_gcal == RequiredCommitAction.Upsert:
                self._handle_gcal_upsert(task)
            elif task.action_gcal == RequiredCommitAction.Delete:
                self._handle_gcal_delete(task)

            # handle requested task action
            if task.action_task == RequiredCommitAction.Upsert:
                self._handle_task_upsert(task)
            elif task.action_task == RequiredCommitAction.Delete:
                self._handle_task_delete(task)

            if (
                task.action_gcal == RequiredCommitAction.Delete
                or task.action_task == RequiredCommitAction.Delete
            ):
                # delete it from the state if delete is requested
                tasks_to_be_deleted.append(task.id)
            else:
                # reset the flags
                task.action_gcal = None
                task.action_task = None

        # finally remove tasks from state list
        for k in tasks_to_be_deleted:
            del self.tasks[k]

        print("State: ", self.tasks)

    def _handle_gcal_upsert(self, task: Task):
        print("Gcal upsert for ", task.id)
        self.cal.upsert_task(task)

    def _handle_gcal_delete(self, task: Task):
        print("Gcal delete for ", task.id)
        self.cal.delete_task(task)

    def _handle_task_upsert(self, task: Task):
        raise NotImplementedError()

    def _handle_task_delete(self, task: Task):
        raise NotImplementedError()
