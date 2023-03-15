import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { TasksController } from "./tasks.controller";
import { TasksService } from "./tasks.service";
import { TasksGateway } from "./tasks.gateway";
import { EventEmitterModule } from "@nestjs/event-emitter";
import { JwtStrategy } from "./jwt.strategy";
import { ScheduleModule } from "@nestjs/schedule";

@Module({
  controllers: [TasksController],
  providers: [TasksService, TasksGateway, JwtStrategy],
  imports: [
    ConfigModule.forRoot(),
    EventEmitterModule.forRoot(),
    ScheduleModule.forRoot(),
  ],
})
export class TasksModule {}
