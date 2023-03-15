import { NestFactory } from "@nestjs/core";
import { DocumentBuilder } from "@nestjs/swagger";
import { SwaggerModule } from "@nestjs/swagger/dist";
import { TasksModule } from "./tasks.module";

async function bootstrap() {
  const app = await NestFactory.create(TasksModule);

  const swagger_conf = new DocumentBuilder()
    .setTitle("Tasks")
    .setDescription("Notion based Task List API")
    .setVersion("0.0.1")
    .build();
  const doc = SwaggerModule.createDocument(app, swagger_conf);
  SwaggerModule.setup("api", app, doc);

  await app.listen(3000);
}
bootstrap();
