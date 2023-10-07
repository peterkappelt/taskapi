import Image from "next/image";
import notion_icon from "./notion.svg";

type ImageProps = React.ComponentProps<typeof Image>;

const NotionIcon = (props: Omit<ImageProps, "src" | "alt">): JSX.Element => {
  return <Image {...props} src={notion_icon} alt="Notion Icon" />;
};

export default NotionIcon;
