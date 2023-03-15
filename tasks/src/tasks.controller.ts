import {
  Body,
  Controller,
  Get,
  HttpException,
  HttpStatus,
  Logger,
  Param,
  Post,
} from "@nestjs/common";
import { TasksService } from "./tasks.service";
import { TTask } from "./types";

const uuid_regex = new RegExp(
  /^[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i,
);

@Controller("tasks")
export class TasksController {
  private readonly logger = new Logger(TasksController.name);

  constructor(private readonly tasksService: TasksService) {}

  //@UseGuards(AuthGuard("jwt"))
  @Get()
  async getTasks(): Promise<TTask[]> {
    try {
      const tasks = await this.tasksService.getTasks();
      return tasks;
    } catch (ex) {
      throw new HttpException(
        { message: "DB_FETCH_FAILED", reason: ex.toString() },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  //@UseGuards(AuthGuard("jwt"))
  @Get(":id")
  async getTask(@Param("id") id: string): Promise<TTask> {
    if (!id || !uuid_regex.test(id))
      throw new HttpException(
        {
          message: "BAD_REQUEST",
          reason: "id must be given and id must be uuid",
        },
        HttpStatus.BAD_REQUEST,
      );

    try {
      return await this.tasksService.getTask(id);
    } catch (ex) {
      throw new HttpException(
        { message: "NOT_FOUND", reason: "Task not found" },
        HttpStatus.NOT_FOUND,
      );
    }
  }

  //@UseGuards(AuthGuard("jwt"))
  @Post("find")
  async findTaskByTitle(@Body("title") title?: string): Promise<TTask[]> {
    if (!title)
      throw new HttpException(
        {
          message: "BAD_REQUEST",
          reason: "title must be given",
        },
        HttpStatus.BAD_REQUEST,
      );

    try {
      const tasks = await this.tasksService.findTaskByTitle(title);
      return tasks;
    } catch (ex) {
      throw new HttpException(
        { message: "DB_FETCH_FAILED", reason: ex.toString() },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
