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

const GoogleTasklistPicker = <
  TFieldValues extends FieldValues = FieldValues,
  TName extends Path<TFieldValues> = Path<TFieldValues>
>({
  field,
  lists,
}: {
  field: TextInputProps<TFieldValues, TName>;
  lists?: { id?: string; title?: string }[];
}) => {
  return (
    <Select onValueChange={field.onChange} defaultValue={field.value}>
      <FormControl>
        <SelectTrigger>
          <SelectValue placeholder="Select task list" />
        </SelectTrigger>
      </FormControl>
      <SelectContent>
        {lists && lists.length > 0 ? (
          lists.map((d) => (
            <SelectItem key={d.id} value={d.id ?? "_unknown"}>
              {d.title}
            </SelectItem>
          ))
        ) : (
          <SelectGroup>
            <SelectLabel>No Task Lists available</SelectLabel>
          </SelectGroup>
        )}
      </SelectContent>
    </Select>
  );
};

export default GoogleTasklistPicker;
