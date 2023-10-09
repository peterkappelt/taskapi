import {
  Configuration,
  Me,
  ResponseError,
  SyncConfig,
  TasksApi,
} from "@/apigen";
import { ApiProvider } from "@/components/ApiContext";
import GoogleLoginCard from "@/components/GoogleLoginCard";
import { InvisiblePostFormProvider } from "@/components/InvisiblePostForm";
import NotionLoginCard from "@/components/NotionLoginCard";
import SyncConfEditor from "@/components/SyncConf/SyncConfEditor";
import { cookies } from "next/headers";

async function getData(): Promise<{ me?: Me; syncconf?: SyncConfig }> {
  const api = new TasksApi(
    new Configuration({
      basePath: process.env.NEXT_PUBLIC_BACKEND_URL,
      headers: {
        Cookie: cookies().toString(),
      },
    })
  );

  try {
    const me = await api.retrieveMe();

    // for now, only the first sync conf is editable with the frontend
    const [first_syncconf] = await api.listSyncConfigs();
    const syncconf = first_syncconf?.id
      ? await api.retrieveSyncConfig({ id: first_syncconf.id })
      : undefined;

    return { me, syncconf };
  } catch (e) {
    if (e instanceof ResponseError) {
      //TODO logout
      return {};
    }
    throw e;
  }
  return {};
}

export default async function Home() {
  const { me, syncconf } = await getData();

  return (
    <ApiProvider>
      <InvisiblePostFormProvider>
        <div className="grid grid-cols-1 gap-4">
          {!me ? (
            <>
              <NotionLoginCard action="login" />
              <GoogleLoginCard action="login" />
            </>
          ) : (
            <>
              <SyncConfEditor me={me} initialSyncConf={syncconf} />
            </>
          )}
        </div>
      </InvisiblePostFormProvider>
    </ApiProvider>
  );
}
