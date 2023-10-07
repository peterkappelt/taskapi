"use client";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import LoginButton from "./LoginButton";
import useAccountActions from "@/lib/useAccountActions";
import GoogleIcon from "./icons/google";

const GoogleLoginCard = ({ action }: { action: "login" | "connect" }) => {
  const { login, connect } = useAccountActions();
  return (
    <Card>
      <CardHeader>
        <CardTitle>Google</CardTitle>
        <CardDescription>
          Connect and configure your Google Account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <LoginButton
          icon={<GoogleIcon />}
          text="Connect your Google Account"
          onClick={() =>
            action === "login" ? login("google") : connect("google")
          }
        />
      </CardContent>
    </Card>
  );
};

export default GoogleLoginCard;
