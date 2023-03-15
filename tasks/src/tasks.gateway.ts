import { OnEvent } from "@nestjs/event-emitter";
import { WebSocketGateway, WebSocketServer } from "@nestjs/websockets";
import { Server } from "socket.io";
import { TTaskChange } from "./types";

@WebSocketGateway({ namespace: "/events" })
export class TasksGateway {
  @WebSocketServer()
  server: Server;

  @OnEvent("task.changes")
  handleTaskUpdate(changes: TTaskChange[]) {
    changes.map((c) => this.server.emit("task.change", c));
  }
}
