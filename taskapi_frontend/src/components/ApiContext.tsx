"use client";
import { Configuration, RequestContext, TasksApi } from "@/apigen";
import { ReactNode, createContext, useCallback, useContext } from "react";
import Cookies from "universal-cookie";

const ApiContext = createContext<{ api?: TasksApi }>({});
const cookies = new Cookies();

const ApiProvider = ({ children }: { children: ReactNode }) => {
  const appendCsrfMiddleware = useCallback(async (context: RequestContext) => {
    const method = context.init.method?.toUpperCase();
    if (method !== "POST" && method !== "PATCH") return; // only add csrf token to post/ patch requests
    // use existing csrf token if available, otherwise retrieve a new one
    const token =
      cookies.get("csrftoken") || (await api.retrieveCsrf()).csrftoken;
    // set cookie if not already set
    if (!cookies.get("csrftoken"))
      cookies.set("csrftoken", token, {
        secure: true,
        sameSite: "strict",
        path: "/",
      });
    // add csrf token to request headers
    context.init.headers = {
      ...context.init.headers,
      "X-CSRFToken": token,
    };
    return context;
  }, []);

  const api = new TasksApi(
    new Configuration({ basePath: process.env.NEXT_PUBLIC_BACKEND_URL })
  ).withPreMiddleware(appendCsrfMiddleware);
  return <ApiContext.Provider value={{ api }}>{children}</ApiContext.Provider>;
};

const useApi = () => {
  const { api } = useContext(ApiContext);
  if (!api) throw new Error("Can only call useApi() inside ApiProvider");
  return api;
};

export { ApiProvider, useApi };

