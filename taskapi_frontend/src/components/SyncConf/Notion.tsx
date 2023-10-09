"use client";
import { Me, NotionDbInfo, NotionDbList } from "@/apigen";
import NotionDbFieldPicker from "@/components/NotionDbFieldPicker";
import NotionDbPicker from "@/components/NotionDbPicker";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Form,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { TypographyInlineCode } from "@/components/ui/typography_inline_code";
import { zodResolver } from "@hookform/resolvers/zod";
import { LinkIcon, Settings } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { useApi } from "../ApiContext";

const notionConfSchema = z.object({
  notion_db: z.string({ required_error: "Please select a notion database" }),
  notion_db_date_prop_id: z.string(),
  notion_db_done_prop_id: z.string().optional().nullable(),
});

const NotionSyncConf = ({
  me,
  onSave,
  initialValues,
}: {
  me: Me;
  onSave: (args: z.infer<typeof notionConfSchema>) => any;
  initialValues: Partial<z.infer<typeof notionConfSchema>>;
}) => {
  const [notionDbs, setNotionDbs] = useState<NotionDbList[] | undefined>();
  const [dbInfo, setDbInfo] = useState<NotionDbInfo | undefined>();
  const api = useApi();
  const [open, setOpen] = useState(false);
  const form = useForm<z.infer<typeof notionConfSchema>>({
    resolver: zodResolver(notionConfSchema),
    defaultValues: initialValues,
  });

  useEffect(() => {
    // fetch db info when a DB is given by default
    let isActive = true;
    const doFetch = async () => {
      if (!initialValues.notion_db) return;
      const data = await api.retrieveNotionDbInfo({
        db_id: initialValues.notion_db,
      });
      if (!isActive) return;
      setDbInfo(data);
    };
    doFetch();
    return () => {
      isActive;
    };
  }, [initialValues]);

  useEffect(() => {
    // fetch db info when another Notion DB is selected by the form
    let isActive = true;
    const { unsubscribe } = form.watch((value, { name }) => {
      if (name != "notion_db") return;
      const doFetch = async () => {
        if (!value.notion_db) {
          setDbInfo(undefined);
          return;
        }
        const data = await api.retrieveNotionDbInfo({ db_id: value.notion_db });
        if (!isActive) return;

        setDbInfo(data);
      };
      doFetch();
    });
    return () => {
      unsubscribe();
      isActive = false;
    };
  }, [form.watch]);

  useEffect(() => {
    //automatically choose first date field
    const date_fields = Object.entries(dbInfo?.date_fields || {});
    if (date_fields.length) {
      form.setValue("notion_db_date_prop_id", date_fields[0][0]);
    }
  }, [dbInfo]);

  useEffect(() => {
    let isActive = true;
    const load = async () => {
      const data = await api.listNotionDbLists();
      if (!isActive) return;
      setNotionDbs(data);
    };
    load();
    return () => {
      isActive = false;
    };
  }, []);

  return (
    <Card>
      <Collapsible open={open} onOpenChange={setOpen}>
        <CardHeader className="grid grid-cols-[1fr_auto] items-start gap-4 space-y-0">
          <div className="space-y-1">
            <CardTitle>Notion</CardTitle>
            <CardDescription>Configure your Notion Account</CardDescription>
          </div>
          <CollapsibleTrigger asChild>
            <Button className="w-8 h-8 p-0">
              <Settings className="h-4 w-4" />
            </Button>
          </CollapsibleTrigger>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4">
            <div className=" flex items-center space-x-4 rounded-md border p-4">
              <LinkIcon />
              <div className="flex-1 space-y-1">
                <p className="text-sm font-medium leading-none">
                  Your Notion account is connected
                </p>
                <p className="text-sm text-muted-foreground">
                  Account name: {me.notion}
                </p>
              </div>
            </div>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(
                  (args) => onSave(args), //onValid
                  () => setOpen(true) //onInvalid
                )}
                className="space-y-4"
              >
                <FormField
                  control={form.control}
                  name="notion_db"
                  render={({ field }) => (
                    <FormItem className="flex flex-col">
                      <FormLabel>Database</FormLabel>
                      <NotionDbPicker field={field} databases={notionDbs} />
                      <FormDescription>
                        Select Notion Database to be synchronized
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <CollapsibleContent className="space-y-4">
                  <FormField
                    control={form.control}
                    name="notion_db_date_prop_id"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Date Property</FormLabel>
                        <NotionDbFieldPicker
                          field={field}
                          dbFields={
                            dbInfo?.date_fields as Record<string, string>
                          }
                          textEmpty="No date fields available"
                          textPlaceholder="Select date field of database"
                        />
                        <FormDescription>
                          Select a field of type{" "}
                          <TypographyInlineCode>date</TypographyInlineCode> that
                          represents the due date
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="notion_db_done_prop_id"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Done Property</FormLabel>
                        <NotionDbFieldPicker
                          field={field}
                          dbFields={
                            dbInfo?.checkbox_fields as Record<string, string>
                          }
                          textEmpty="No checkbox fields available"
                          textPlaceholder="Select checkbox field of database"
                        />
                        <FormDescription>
                          Select a field of type{" "}
                          <TypographyInlineCode>checkbox</TypographyInlineCode>{" "}
                          that indicates whether the task is done (optional)
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </CollapsibleContent>
                <Button type="submit">Save</Button>
              </form>
            </Form>
          </div>
        </CardContent>
      </Collapsible>
    </Card>
  );
};

export default NotionSyncConf;
