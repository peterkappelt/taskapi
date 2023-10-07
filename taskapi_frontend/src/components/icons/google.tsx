import Image from "next/image";
import google_icon from "./google.svg";

type ImageProps = React.ComponentProps<typeof Image>;

const GoogleIcon = (props: Omit<ImageProps, "src" | "alt">): JSX.Element => {
  return <Image {...props} src={google_icon} alt="Notion Icon" />;
};

export default GoogleIcon;
