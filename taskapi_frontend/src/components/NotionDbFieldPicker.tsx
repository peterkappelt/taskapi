import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ControllerRenderProps, FieldValues, Path } from "react-hook-form";
import { FormControl } from "./ui/form";
interface TextInputProps<
  TFieldValues extends FieldValues = FieldValues,
  TName extends Path<TFieldValues> = Path<TFieldValues>
> extends ControllerRenderProps<TFieldValues, TName> {}

const NotionDbFieldPicker = <
  TFieldValues extends FieldValues = FieldValues,
  TName extends Path<TFieldValues> = Path<TFieldValues>
>({
  field,
  dbFields,
  textPlaceholder,
  textEmpty,
}: {
  field: TextInputProps<TFieldValues, TName>;
  dbFields?: Record<string, string>;
  textPlaceholder: string;
  textEmpty: string;
}) => {
  
  return (
    <Select
      onValueChange={field.onChange}
      value={field.value}
      defaultValue={field.value}
      disabled={!dbFields}
    >
      <FormControl>
        <SelectTrigger>
          <SelectValue placeholder={textPlaceholder} />
        </SelectTrigger>
      </FormControl>
      <SelectContent>
        {dbFields && Object.keys(dbFields).length > 0 ? (
          Object.entries(dbFields).map(([id, val]) => (
            <SelectItem key={id} value={id}>
              {val}
            </SelectItem>
          ))
        ) : (
          <SelectGroup>
            <SelectLabel>{textEmpty}</SelectLabel>
          </SelectGroup>
        )}
      </SelectContent>
    </Select>
  );
};

export default NotionDbFieldPicker;
