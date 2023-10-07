import { Configuration, Me, ResponseError, TasksApi } from "@/apigen";
import { ApiProvider } from "@/components/ApiContext";
import GoogleLoginCard from "@/components/GoogleLoginCard";
import { InvisiblePostFormProvider } from "@/components/InvisiblePostForm";
import NotionLoginCard from "@/components/NotionLoginCard";
import SyncConfEditor from "@/components/SyncConf/SyncConfEditor";
import { cookies } from "next/headers";

async function getData(): Promise<{ me?: Me }> {
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
    return { me };
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
  const { me } = await getData();

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
              <SyncConfEditor me={me} />
            </>
          )}
        </div>
      </InvisiblePostFormProvider>
    </ApiProvider>
  );
}
