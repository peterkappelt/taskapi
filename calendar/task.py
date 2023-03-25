from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RequiredCommitAction(Enum):
    Upsert = 1
    Delete = 2


@dataclass(eq=False)
class Task:
    id: str
    title: str
    scheduled_start: Optional[str]
    scheduled_end: Optional[str]

    action_gcal: Optional[RequiredCommitAction] = None
    action_task: Optional[RequiredCommitAction] = None

    @staticmethod
    def from_task(task):
        assert "id" in task
        assert "title" in task

        return Task(
            id=task["id"],
            title=task["title"],
            scheduled_start=task.get("scheduled_start", None),
            scheduled_end=task.get("scheduled_end", None),
        )

    @staticmethod
    def from_gcal_event(event):
        raise NotImplementedError()

    def should_be_event(self):
        return self.scheduled_start is not None and self.scheduled_end is not None

    def __eq__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return (
            self.id == other.id
            and self.title == other.title
            and self.scheduled_start == other.scheduled_start
            and self.scheduled_end == other.scheduled_end
        )
