import {
  BrowserViewType,
  StorageDirectoryTableData
} from '../../../../reactComponents/FileChooser/types';
import {
  isHDFS,
  isOFS,
  isABFSRoot,
  isGSRoot,
  isOFSServiceID,
  isOFSVol,
  isS3Root,
  isABFS,
  isGS,
  isS3,
  isOFSRoot,
  inTrash
} from '../../../../utils/storageBrowserUtils';

export enum ActionType {
  Copy = 'copy',
  Move = 'move',
  Summary = 'summary',
  Rename = 'rename',
  Replication = 'replication',
  Delete = 'delete'
}

const isValidFileOrFolder = (filePath: string): boolean => {
  return (
    isHDFS(filePath) ||
    (isS3(filePath) && !isS3Root(filePath)) ||
    (isGS(filePath) && !isGSRoot(filePath)) ||
    (isABFS(filePath) && !isABFSRoot(filePath)) ||
    (isOFS(filePath) && !isOFSRoot(filePath) && !isOFSServiceID(filePath) && !isOFSVol(filePath))
  );
};

const isActionEnabled = (file: StorageDirectoryTableData, action: ActionType): boolean => {
  switch (action) {
    case ActionType.Summary:
      return (isHDFS(file.path) || isOFS(file.path)) && file.type === BrowserViewType.file;
    case ActionType.Replication:
      return isHDFS(file.path) && file.type === BrowserViewType.file;
    case ActionType.Rename:
    case ActionType.Copy:
    case ActionType.Delete:
    case ActionType.Move:
      return isValidFileOrFolder(file.path);
    default:
      return false;
  }
};

const isSingleFileActionEnabled = (
  files: StorageDirectoryTableData[],
  action: ActionType
): boolean => {
  return files.length === 1 && isActionEnabled(files[0], action);
};

const isMultipleFileActionEnabled = (
  files: StorageDirectoryTableData[],
  action: ActionType
): boolean => {
  return files.length !== 0 && files.every(file => isActionEnabled(file, action));
};

export const getEnabledActions = (
  files: StorageDirectoryTableData[]
): {
  enabled: boolean;
  type: ActionType;
  label: string;
}[] => {
  const isAnyFileInTrash = files.some(file => inTrash(file.path));
  const isNoFileSelected = files && files.length === 0;
  if (isAnyFileInTrash || isNoFileSelected) {
    return [];
  }

  // order of the elements will be the order of the action menu
  const actions = [
    {
      enabled: isMultipleFileActionEnabled(files, ActionType.Copy),
      type: ActionType.Copy,
      label: 'Copy'
    },
    {
      enabled: isMultipleFileActionEnabled(files, ActionType.Move),
      type: ActionType.Move,
      label: 'Move'
    },
    {
      enabled: isSingleFileActionEnabled(files, ActionType.Summary),
      type: ActionType.Summary,
      label: 'View Summary'
    },
    {
      enabled: isSingleFileActionEnabled(files, ActionType.Rename),
      type: ActionType.Rename,
      label: 'Rename'
    },
    {
      enabled: isMultipleFileActionEnabled(files, ActionType.Delete),
      type: ActionType.Delete,
      label: 'Delete'
    },
    {
      enabled: isSingleFileActionEnabled(files, ActionType.Replication),
      type: ActionType.Replication,
      label: 'Set Replication'
    }
  ].filter(e => e.enabled);

  return actions;
};
