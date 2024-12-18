import { StorageDirectoryTableData } from '../../../../reactComponents/FileChooser/types';
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
  isOFSRoot
} from '../../../../utils/storageBrowserUtils';

export enum ActionType {
  Copy = 'copy',
  Move = 'move',
  Summary = 'summary',
  Rename = 'rename',
  Repilcation = 'repilcation'
}

const isValidFileOrFolder = (filePath: string) => {
  return (
    isHDFS(filePath) ||
    (isS3(filePath) && !isS3Root(filePath)) ||
    (isGS(filePath) && !isGSRoot(filePath)) ||
    (isABFS(filePath) && !isABFSRoot(filePath)) ||
    (isOFS(filePath) && !isOFSRoot(filePath) && !isOFSServiceID(filePath) && !isOFSVol(filePath))
  );
};

const isSummaryEnabled = (files: StorageDirectoryTableData[]) => {
  if (files.length !== 1) {
    return false;
  }
  const selectedFile = files[0];
  return (isHDFS(selectedFile.path) || isOFS(selectedFile.path)) && selectedFile.type === 'file';
};

const isRenameEnabled = (files: StorageDirectoryTableData[]) => {
  if (files.length !== 1) {
    return false;
  }
  const filePath = files[0].path;
  return isValidFileOrFolder(filePath);
};

const isReplicationEnabled = (files: StorageDirectoryTableData[]) => {
  if (files.length !== 1) {
    return false;
  }
  const selectedFile = files[0];
  return isHDFS(selectedFile.path) && selectedFile.type === 'file';
};

const isCopyEnabled = (files: StorageDirectoryTableData[]) => {
  if (files.length > 0) {
    const filePath = files[0].path;
    return isValidFileOrFolder(filePath);
  }
  return false;
};

const isMoveEnabled = (files: StorageDirectoryTableData[]) => {
  if (files.length > 0) {
    const filePath = files[0].path;
    return isValidFileOrFolder(filePath);
  }
  return false;
};

export const getActionsConfig = (files: StorageDirectoryTableData[]): Record<string, boolean> => {
  return {
    isSummaryEnabled: isSummaryEnabled(files),
    isRenameEnabled: isRenameEnabled(files),
    isReplicationEnabled: isReplicationEnabled(files),
    isCopyEnabled: isCopyEnabled(files),
    isMoveEnabled: isMoveEnabled(files)
  };
};
