import { GTasksTasklists, Me } from "@/apigen";
import { useApi } from "@/components/ApiContext";
import GoogleTasklistPicker from "@/components/GoogleTasklistPicker";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { zodResolver } from "@hookform/resolvers/zod";
import { LinkIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import * as z from "zod";

const gTasksConfSchema = z.object({
  g_tasks_tasklist: z.string({ required_error: "Pleases select a tasklist" }).nullable(),
});

const GoogleSyncConf = ({
  me,
  onSave,
  initialValues,
}: {
  me: Me;
  onSave: (args: z.infer<typeof gTasksConfSchema>) => any;
  initialValues: Partial<z.infer<typeof gTasksConfSchema>>;
}) => {
  const [tasklists, setTasklists] = useState<GTasksTasklists[] | undefined>();
  const api = useApi();

  const gTasksForm = useForm<z.infer<typeof gTasksConfSchema>>({
    resolver: zodResolver(gTasksConfSchema),
    defaultValues: initialValues,
  });

  useEffect(() => {
    let isActive = true;
    const load = async () => {
      if (!api) return;
      const data = await api.listGTasksTasklists();
      if (!isActive) return;
      setTasklists(data);
    };
    load();
    return () => {
      isActive = false;
    };
  }, [api]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Google</CardTitle>
        <CardDescription>Configure your Google Account</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-4">
          <div className=" flex items-center space-x-4 rounded-md border p-4">
            <LinkIcon />
            <div className="flex-1 space-y-1">
              <p className="text-sm font-medium leading-none">
                Your Google account is connected
              </p>
              <p className="text-sm text-muted-foreground">
                Account name: {me.g_tasks}
              </p>
            </div>
          </div>
          <Form {...gTasksForm}>
            <form
              onSubmit={gTasksForm.handleSubmit((args) => onSave(args))}
              className="space-y-4"
            >
              <FormField
                control={gTasksForm.control}
                name="g_tasks_tasklist"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Task List</FormLabel>
                    <GoogleTasklistPicker field={field} lists={tasklists} />
                    <FormDescription>
                      Select Google Task List to be synchronized
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit">Save</Button>
            </form>
          </Form>
        </div>
      </CardContent>
    </Card>
  );
};

export default GoogleSyncConf;
