import { useInvisiblePostForm } from "@/components/InvisiblePostForm";

type TProviders = "google" | "taskapi_notion";

const useAccountActions = () => {
  const { submit } = useInvisiblePostForm();

  return {
    login: (provider: TProviders) => {
      // TOOD validate whether this is prone to CSRF
      submit(
        `/accounts/${provider}/login/?process=login&next=${encodeURIComponent(
          window.location.pathname
        )}`
      );
    },
    connect: (provider: TProviders) => {
      submit(
        `/accounts/${provider}/login/?process=connect&next=${encodeURIComponent(
          window.location.pathname
        )}`
      );
    },
    logout: () => {
      submit(
        `/accounts/logout/?next=${encodeURIComponent(window.location.pathname)}`
      );
    },
  };
};

export default useAccountActions;
