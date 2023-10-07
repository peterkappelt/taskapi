import React, { ReactElement } from "react";
import { Button } from "./ui/button";

type ButtonOnClickType = React.ComponentProps<typeof Button>["onClick"];

const LoginButton = ({
  icon,
  text,
  onClick,
}: {
  icon: ReactElement;
  text: string;
  onClick?: ButtonOnClickType;
}): JSX.Element => {
  return (
    <div className="container w-full px-0 flex">
    <Button variant="default" className="w-full max-w-md mx-auto" onClick={onClick}>
      {React.cloneElement(icon, { className: "mr-2 h-4 w-4" })}
      {text}
    </Button>
    </div>
  );
};

export default LoginButton;
