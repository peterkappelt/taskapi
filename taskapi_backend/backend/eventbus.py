from dataclasses import dataclass
from abc import ABC
from typing import Callable, Literal, Tuple, Type
from .models import SyncConfig, SyncedRecord


@dataclass
class Event(ABC):
    pass


@dataclass
class EventRecordChanged(Event):
    sender: Literal["notion"] | Literal["g_tasks"]
    conf: SyncConfig
    record: SyncedRecord


class _EventBus:
    listeners: Tuple[Type[Event], Callable[[Event], None]] = []

    def subscribe(self, event_type: Type[Event], callback: Callable[[Event], None]):
        self.listeners.append((event_type, callback))

    def publish(self, event: Event):
        for event_type, callback in self.listeners:
            if isinstance(event, event_type):
                callback(event)


EventBus = _EventBus()
