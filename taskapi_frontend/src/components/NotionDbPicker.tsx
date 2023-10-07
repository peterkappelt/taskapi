import { FormControl } from "@/components/ui/form";
import { ControllerRenderProps, FieldValues, Path } from "react-hook-form";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface TextInputProps<
  TFieldValues extends FieldValues = FieldValues,
  TName extends Path<TFieldValues> = Path<TFieldValues>
> extends ControllerRenderProps<TFieldValues, TName> {}

const NotionDbPicker = <
  TFieldValues extends FieldValues = FieldValues,
  TName extends Path<TFieldValues> = Path<TFieldValues>
>({
  field,
  databases,
}: {
  field: TextInputProps<TFieldValues, TName>;
  databases?: { id?: string; title?: string }[];
}) => {
  return (
    <Select onValueChange={field.onChange} defaultValue={field.value}>
      <FormControl>
        <SelectTrigger>
          <SelectValue placeholder="Select database" />
        </SelectTrigger>
      </FormControl>
      <SelectContent>
        {databases && databases.length > 0 ? (
          databases.map((d) => (
            <SelectItem key={d.id} value={d.id ?? "_unknown"}>{d.title}</SelectItem>
          ))
        ) : (
          <SelectGroup>
            <SelectLabel>No Databases available</SelectLabel>
          </SelectGroup>
        )}
      </SelectContent>
    </Select>
  );
};

export default NotionDbPicker;
