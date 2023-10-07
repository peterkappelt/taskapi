"use client";
import {
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useRef,
} from "react";

type TInvisiblePostForm = {
  submit: (action: string) => any;
};

const InvisiblePostFormContext = createContext<TInvisiblePostForm>({
  submit: (action: string) => null,
});

export function InvisiblePostFormProvider({
  children,
}: {
  children: ReactNode;
}) {
  const formRef = useRef<HTMLFormElement>(null);
  const submit = useCallback((action: string) => {
    const form = formRef.current;
    if (!form) {
      alert("Internal bug: can't submit form. Please report!");
      return;
    }
    form.action = action;
    form.submit();
  }, []);

  return (
    <>
      <form style={{ visibility: "hidden" }} method="POST" ref={formRef} />
      <InvisiblePostFormContext.Provider value={{ submit }}>
        {children}
      </InvisiblePostFormContext.Provider>
    </>
  );
}

export const useInvisiblePostForm = () => useContext(InvisiblePostFormContext);
