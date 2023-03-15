export type TTask = {
  id: string;
  title: string;
  deadline?: Date;
  scheduled_start?: Date;
  scheduled_end?: Date;
};

export enum TTaskChange_Type {
  New,
  Update,
  Delete,
}

type TTaskChange_AddOrUpdate = {
  type: TTaskChange_Type.New | TTaskChange_Type.Update;
  task: TTask;
};

type TTaskChange_Delete = {
  type: TTaskChange_Type.Delete;
};

export type TTaskChange = {
  id: string;
} & (TTaskChange_AddOrUpdate | TTaskChange_Delete);
