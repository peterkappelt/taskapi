"use client";

import { Me, SyncConfig } from "@/apigen";
import { useApi } from "@/components/ApiContext";
import { AlertCircle, CheckCircle, Info } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import GoogleLoginCard from "../GoogleLoginCard";
import NotionLoginCard from "../NotionLoginCard";
import { TypographyInlineCode } from "../ui/typography_inline_code";
import GoogleSyncConf from "./Google";
import NotionSyncConf from "./Notion";

type PartialSyncConfig = Partial<SyncConfig>;

interface SyncConfigValidationResult {
  valid: boolean;
  missing: {
    notion?: boolean;
    g_tasks?: boolean;
    notion_db?: boolean;
    notion_db_date_prop_id?: boolean;
    g_tasks_tasklist?: boolean;
  };
}

const validateSyncConf = (
  me: Me,
  conf: PartialSyncConfig
): SyncConfigValidationResult => {
  const missing = {
    notion: !me.notion,
    g_tasks: !me.g_tasks,
    notion_db: !conf.notion_db,
    notion_db_date_prop_id: !conf.notion_db_date_prop_id,
    g_tasks_tasklist: !conf.g_tasks_tasklist,
  };
  return {
    valid: !Object.values(missing).some((v) => v),
    missing,
  };
};

const syncConfIsValid = (me: Me, conf: PartialSyncConfig): conf is SyncConfig =>
  validateSyncConf(me, conf).valid;

const MissingHint = ({
  me,
  conf,
  validation,
}: {
  me: Me;
  conf: PartialSyncConfig;
  validation: SyncConfigValidationResult;
}) => {
  let icon: JSX.Element;
  let message_header: JSX.Element | string;
  let message_body: JSX.Element | string;

  if (validation.missing.notion) {
    icon = <AlertCircle className="text-red-500" size={24} />;
    message_header = "Notion not connected";
    message_body = "Please connect your notion account to proceed.";
  } else if (validation.missing.g_tasks) {
    icon = <AlertCircle className="text-red-500" size={24} />;
    message_header = "Google Tasks not connected";
    message_body = "Please connect your Google account to proceed.";
  } else if (validation.missing.notion_db) {
    icon = <Info size={24} className="text-red-500" />;
    message_header = "Configure Notion";
    message_body = "Please select a Notion Database to get started.";
  } else if (validation.missing.notion_db_date_prop_id) {
    icon = <Info size={24} className="text-red-500" />;
    message_header = "Configure Notion";
    message_body =
      "Select a date property from your Notion Database to get started";
  } else if (validation.missing.g_tasks_tasklist) {
    icon = <Info size={24} className="text-red-500" />;
    message_header = "Configure Google";
    message_body = "Select a Google Task List to get started";
  } else {
    icon = <CheckCircle className="text-green-500" size={24} />;
    message_header = "All set!";
    message_body = (
      <>
        Your Notion Database will now be synchronized with Google Tasks (and
        vice versa).
        <br />
        Please note that it'll take up to{" "}
        <TypographyInlineCode>2</TypographyInlineCode> minutes for any updates
        to synchronize.
      </>
    );
  }
  return (
    <div className=" flex items-center space-x-4 rounded-md border p-4">
      {icon}
      <div className="flex-1 space-y-1">
        <p className="text-sm font-medium leading-none">{message_header}</p>
        <p className="text-sm text-muted-foreground">{message_body}</p>
      </div>
    </div>
  );
};

const SyncConfEditor = ({ me }: { me: Me }) => {
  const [conf, setConf] = useState<PartialSyncConfig>({});
  const validation = useMemo(() => validateSyncConf(me, conf), [me, conf]);
  const api = useApi();

  const handleFormSave = useCallback(
    async (incoming: PartialSyncConfig) => {
      const complete = { ...conf, ...incoming };

      if (!syncConfIsValid(me, complete)) {
        setConf(complete); //update the partial conf, but don't do API call
        return;
      }
      
      let res: SyncConfig;
      if (complete.id) {
        // id is set -> conf exists -> patch
        res = await api.partialUpdateSyncConfig({
          id: complete.id,
          SyncConfig: complete,
        });
      } else {
        // no id set -> create
        res = await api.createSyncConfig({
          SyncConfig: complete,
        });
      }
      setConf(res);
    },
    [conf, validation]
  );

  return (
    <>
      {validation.missing.notion ? <NotionLoginCard action="connect" /> : null}
      {validation.missing.g_tasks ? <GoogleLoginCard action="connect" /> : null}
      {!validation.missing.notion ? (
        <NotionSyncConf me={me} onSave={handleFormSave} />
      ) : null}
      {!validation.missing.g_tasks ? (
        <GoogleSyncConf me={me} onSave={handleFormSave} />
      ) : null}
      <MissingHint me={me} conf={conf} validation={validation} />
    </>
  );
};

export default SyncConfEditor;
