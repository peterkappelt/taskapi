"use client";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import LoginButton from "./LoginButton";
import NotionIcon from "./icons/notion";
import useAccountActions from "@/lib/useAccountActions";

const NotionLoginCard = ({ action }: { action: "login" | "connect" }) => {
  const { login, connect } = useAccountActions();
  return (
    <Card>
      <CardHeader>
        <CardTitle>Notion</CardTitle>
        <CardDescription>
          Connect and configure your Notion Account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <LoginButton
          icon={<NotionIcon />}
          text="Connect your Notion Account"
          onClick={() =>
            action === "login"
              ? login("taskapi_notion")
              : connect("taskapi_notion")
          }
        />
      </CardContent>
      {/*<CardFooter>
        </CardFooter>*/}
    </Card>
  );
};

export default NotionLoginCard;
