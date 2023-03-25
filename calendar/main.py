import os
import socketio
from state import State

EVENT_WEBSOCKET_ENDPOINT = os.environ["EVENT_WEBSOCKET_ENDPOINT"]


def main():
    state = State()

    sio = socketio.Client(logger=True)

    @sio.on("task.change", namespace="/events")  # pyright: reportOptionalCall=false
    def on_task_change(data):
        state.handle_task_change(data)
        state.commit()

    sio.connect(EVENT_WEBSOCKET_ENDPOINT, namespaces=["/events"])
    sio.wait()


if __name__ == "__main__":
    main()
