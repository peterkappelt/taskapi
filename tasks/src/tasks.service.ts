import { Injectable, Logger } from "@nestjs/common";
import { ConfigService } from "@nestjs/config/dist";
import { Client } from "@notionhq/client";
import {
  PageObjectResponse,
  PartialPageObjectResponse,
  QueryDatabaseParameters,
} from "@notionhq/client/build/src/api-endpoints";
import { TTask, TTaskChange, TTaskChange_Type } from "./types";
import { isDeepStrictEqual } from "util";
import { Interval } from "@nestjs/schedule";
import { EventEmitter2 } from "@nestjs/event-emitter";

class NotionDbAdapter {
  private notion: Client;

  constructor(token: string, private db_id: string) {
    this.notion = new Client({
      auth: token,
    });
  }

  #to_date_or_undefined = (
    input: string | undefined | null,
  ): Date | undefined => {
    return input ? new Date(input) : undefined;
  };

  #convert_page = (
    page: PageObjectResponse | PartialPageObjectResponse,
  ): TTask => {
    if (!("parent" in page)) {
      throw new Error(
        "NotionDB: Partial page was returned, this is unexpected",
      );
    }

    const {
      id,
      properties: {
        Title: title,
        Deadline: deadline,
        Scheduled: scheduled,
        Status: status,
        Parent: parent,
        Subtasks: subtasks,
      },
    } = page;

    if (!title || title.type !== "title")
      throw new Error("Invalid Title field");
    if (!deadline || deadline.type !== "date")
      throw new Error("Invalid Deadline field");
    if (!scheduled || scheduled.type !== "date")
      throw new Error("Invalid Scheduled field");
    if (!status || status.type !== "status")
      throw new Error("Invalid Status field");
    if (!parent || parent.type !== "relation")
      throw new Error("Invalid Parent field");
    if (!subtasks || subtasks.type !== "relation")
      throw new Error("Invalid Subtasks field");

    return {
      id,
      title: title.title[0]?.plain_text ?? "", //title might be undefined, for instance when user is currently creating it
      deadline: this.#to_date_or_undefined(deadline.date?.start),
      scheduled_start: this.#to_date_or_undefined(scheduled.date?.start),
      scheduled_end: this.#to_date_or_undefined(scheduled.date?.end),
    };
  };

  async query(
    filter: QueryDatabaseParameters["filter"] = undefined,
  ): Promise<TTask[]> {
    const res = await this.notion.databases.query({
      database_id: this.db_id,
      filter,
    });

    return res.results.map(this.#convert_page);
  }

  async getTask(id: string): Promise<TTask> {
    const res = await this.notion.pages.retrieve({
      page_id: id,
    });
    return this.#convert_page(res);
  }
}

@Injectable()
export class TasksService {
  private readonly logger = new Logger(TasksService.name);
  private notion: NotionDbAdapter;
  private lastState: TTask[];
  private lastStateInitialized = false;

  constructor(
    configService: ConfigService,
    private eventEmitter: EventEmitter2,
  ) {
    const token = configService.get<string>("NOTION_TOKEN");
    const db = configService.get<string>("NOTION_DB");
    if (!db || !token)
      throw new Error("NOTION_TOKEN and NOTION_DB must be specified");
    this.notion = new NotionDbAdapter(token, db);
  }

  async getTasks(): Promise<TTask[]> {
    //TODO check pagination
    return this.notion.query();
  }

  async findTaskByTitle(title: string): Promise<TTask[]> {
    return this.notion.query({
      property: "Title",
      rich_text: { contains: title },
    });
  }

  async getTask(id: string): Promise<TTask> {
    return this.notion.getTask(id);
  }

  async getChanges(): Promise<TTaskChange[]> {
    const current_tasks = await this.notion.query();
    let changes: TTaskChange[] = [];

    if (!this.lastState) {
      //initialize and don't calculate diff if it's the first run
      this.lastState = current_tasks;
      return [];
    }

    // newly created tasks
    const new_tasks = current_tasks.filter(
      (t) => !this.lastState.some((c) => c.id == t.id),
    );
    changes = changes.concat(
      new_tasks.map((t) => ({
        id: t.id,
        type: TTaskChange_Type.New,
        task: t,
      })),
    );

    // deleted tasks
    const deleted_tasks = this.lastState.filter(
      (t) => !current_tasks.some((c) => c.id == t.id),
    );
    changes = changes.concat(
      deleted_tasks.map((t) => ({
        id: t.id,
        type: TTaskChange_Type.Delete,
      })),
    );

    // changed tasks
    const changed_tasks = this.lastState
      .map((task) => {
        const other = current_tasks.find((o) => o.id == task.id);
        if (!isDeepStrictEqual(task, other)) return other;
      })
      .filter((t): t is TTask => t !== undefined);
    changes = changes.concat(
      changed_tasks.map((t) => ({
        id: t.id,
        type: TTaskChange_Type.Update,
        task: t,
      })),
    );

    // update the cache
    this.lastState = current_tasks;
    return changes;
  }

  @Interval(2 * 1000)
  async updateTaskCache() {
    const changes = await this.getChanges();
    if (!changes.length) return;

    this.logger.debug(`Found ${changes.length} changes`);
    this.eventEmitter.emit("task.changes", changes);
  }
}
