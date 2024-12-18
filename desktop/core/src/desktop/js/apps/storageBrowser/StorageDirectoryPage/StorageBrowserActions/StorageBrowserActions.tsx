// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, { useCallback, useMemo, useState } from 'react';
import { Dropdown } from 'antd';
import { MenuItemType } from 'antd/lib/menu/hooks/useItems';

import Button from 'cuix/dist/components/Button';
import DropDownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';
import InfoIcon from '@cloudera/cuix-core/icons/react/InfoIcon';
import DuplicateIcon from '@cloudera/cuix-core/icons/react/DuplicateIcon';
import CopyClipboardIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';

import { i18nReact } from '../../../../utils/i18nReact';
import {
  isHDFS,
  isOFS,
  isABFSRoot,
  isGSRoot,
  isOFSServiceID,
  isOFSVol,
  isS3Root,
  inTrash,
  isABFS,
  isGS,
  isS3,
  isOFSRoot
} from '../../../../utils/storageBrowserUtils';
import {
  RENAME_API_URL,
  SET_REPLICATION_API_URL,
  BULK_COPY_API_URL,
  BULK_MOVE_API_URL
} from '../../../../reactComponents/FileChooser/api';
import huePubSub from '../../../../utils/huePubSub';
import useSaveData from '../../../../utils/hooks/useSaveData';

import SummaryModal from '../SummaryModal/SummaryModal';
import InputModal from '../../InputModal/InputModal';
import FileChooserModal from '../../FileChooserModal/FileChooserModal';

import './StorageBrowserActions.scss';
import { StorageDirectoryTableData } from '../../../../reactComponents/FileChooser/types';

interface StorageBrowserRowActionsProps {
  currentPath: string;
  selectedFiles: StorageDirectoryTableData[];
  onSuccessfulAction: () => void;
  setLoadingFiles: (value: boolean) => void;
}

const StorageBrowserActions = ({
  currentPath,
  selectedFiles,
  onSuccessfulAction,
  setLoadingFiles
}: StorageBrowserRowActionsProps): JSX.Element => {
  const [showSummaryModal, setShowSummaryModal] = useState<boolean>(false);
  const [showRenameModal, setShowRenameModal] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [showReplicationModal, setShowReplicationModal] = useState<boolean>(false);
  const [showCopyModal, setShowCopyModal] = useState<boolean>(false);
  const [showMoveModal, setShowMoveModal] = useState<boolean>(false);

  const { t } = i18nReact.useTranslation();

  const { error: renameError, save: saveRename } = useSaveData(RENAME_API_URL);

  const handleRename = (value: string) => {
    setLoadingFiles(true);
    saveRename(
      { source_path: selectedFile, destination_path: value },
      {
        onSuccess: () => {
          setLoadingFiles(false);
          onSuccessfulAction();
        },
        onError: () => {
          huePubSub.publish('hue.error', renameError);
          setLoadingFiles(false);
        }
      }
    );
  };

  const { error: replicationError, save: saveReplication } = useSaveData(SET_REPLICATION_API_URL);
  const handleReplication = (replicationFactor: number) => {
    saveReplication(
      { path: selectedFile, replication_factor: replicationFactor },
      {
        onSuccess: () => onSuccessfulAction(),
        onError: () => {
          huePubSub.publish('hue.error', replicationError);
        }
      }
    );
  };

  const { error: bulkCopyError, save: saveBulkCopy } = useSaveData(BULK_COPY_API_URL, {
    postOptions: {
      qsEncodeData: false,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  });

  const handleCopy = (destination_path: string) => {
    setLoadingFiles(true);
    const formData = new FormData();
    selectedFiles.map(selectedFile => {
      formData.append('source_path', selectedFile.path);
    });
    formData.append('destination_path', destination_path);
    saveBulkCopy(formData, {
      onSuccess: () => {
        setLoadingFiles(false);
        onSuccessfulAction();
      },
      onError: () => {
        huePubSub.publish('hue.error', bulkCopyError);
        setLoadingFiles(false);
      }
    });
  };

  const { error: bulkMoveError, save: saveBulkMove } = useSaveData(BULK_MOVE_API_URL, {
    postOptions: {
      qsEncodeData: false,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  });

  const handleMove = (destination_path: string) => {
    setLoadingFiles(true);
    const formData = new FormData();
    selectedFiles.map(selectedFile => {
      formData.append('source_path', selectedFile.path);
    });
    formData.append('destination_path', destination_path);
    saveBulkMove(formData, {
      onSuccess: () => {
        setLoadingFiles(false);
        onSuccessfulAction();
      },
      onError: () => {
        huePubSub.publish('hue.error', bulkMoveError);
        setLoadingFiles(false);
      }
    });
  };

  const isValidFileOrFolder = (selectedFilePath: string) => {
    return (
      isHDFS(selectedFilePath) ||
      (isS3(selectedFilePath) && !isS3Root(selectedFilePath)) ||
      (isGS(selectedFilePath) && !isGSRoot(selectedFilePath)) ||
      (isABFS(selectedFilePath) && !isABFSRoot(selectedFilePath)) ||
      (isOFS(selectedFilePath) &&
        !isOFSRoot(selectedFilePath) &&
        !isOFSServiceID(selectedFilePath) &&
        !isOFSVol(selectedFilePath))
    );
  };

  const isSummaryEnabled = useMemo(() => {
    if (selectedFiles.length !== 1) {
      return false;
    }
    const selectedFile = selectedFiles[0];
    return (isHDFS(selectedFile.path) || isOFS(selectedFile.path)) && selectedFile.type === 'file';
  }, [selectedFiles]);

  const isRenameEnabled = useMemo(() => {
    if (selectedFiles.length !== 1) {
      return false;
    }
    const selectedFilePath = selectedFiles[0].path;
    return isValidFileOrFolder(selectedFilePath);
  }, [selectedFiles]);

  const isReplicationEnabled = useMemo(() => {
    if (selectedFiles.length !== 1) {
      return false;
    }
    const selectedFile = selectedFiles[0];
    return isHDFS(selectedFile.path) && selectedFile.type === 'file';
  }, [selectedFiles]);

  const isCopyEnabled = useMemo(() => {
    if (selectedFiles.length > 0) {
      const selectedFilePath = selectedFiles[0].path;
      return isValidFileOrFolder(selectedFilePath);
    }
    return false;
  }, [selectedFiles]);

  const isMoveEnabled = useMemo(() => {
    if (selectedFiles.length > 0) {
      const selectedFilePath = selectedFiles[0].path;
      return isValidFileOrFolder(selectedFilePath);
    }
    return false;
  }, [selectedFiles]);

  const getActions = useCallback(() => {
    const actions: MenuItemType[] = [];
    if (selectedFiles && selectedFiles.length > 0 && !inTrash(selectedFiles[0].path)) {
      if (isCopyEnabled) {
        actions.push({
          key: 'copy',
          icon: <CopyClipboardIcon />,
          label: t('Copy'),
          onClick: () => {
            setSelectedFile(selectedFiles[0].path);
            setShowCopyModal(true);
          }
        });
      }
      if (isMoveEnabled) {
        actions.push({
          key: 'move',
          icon: <CopyClipboardIcon />,
          label: t('Move'),
          onClick: () => {
            setSelectedFile(selectedFiles[0].path);
            setShowMoveModal(true);
          }
        });
      }
      if (isSummaryEnabled) {
        actions.push({
          key: 'content_summary',
          icon: <InfoIcon />,
          label: t('View Summary'),
          onClick: () => {
            setSelectedFile(selectedFiles[0].path);
            setShowSummaryModal(true);
          }
        });
      }
      if (isRenameEnabled) {
        actions.push({
          key: 'rename',
          icon: <InfoIcon />,
          label: t('Rename'),
          onClick: () => {
            setSelectedFile(selectedFiles[0].path);
            setShowRenameModal(true);
          }
        });
      }
      if (isReplicationEnabled) {
        actions.push({
          key: 'setReplication',
          icon: <DuplicateIcon />,
          label: t('Set Replication'),
          onClick: () => {
            setSelectedFile(selectedFiles[0].path);
            setShowReplicationModal(true);
          }
        });
      }
    }
    return actions;
  }, [
    selectedFiles,
    isSummaryEnabled,
    isRenameEnabled,
    isReplicationEnabled,
    isCopyEnabled,
    currentPath
  ]);

  return (
    <>
      <Dropdown
        overlayClassName="hue-storage-browser__table-actions-dropdown"
        menu={{
          items: getActions(),
          className: 'hue-storage-browser__table-actions-menu'
        }}
        trigger={['click']}
        disabled={getActions().length === 0 ? true : false}
      >
        <Button data-event="">
          {t('Actions')}
          <DropDownIcon />
        </Button>
      </Dropdown>
      <SummaryModal
        showModal={showSummaryModal}
        path={selectedFile}
        onClose={() => setShowSummaryModal(false)}
      />
      <InputModal
        title={t('Rename')}
        inputLabel={t('Enter new name here')}
        submitText={t('Rename')}
        showModal={showRenameModal}
        onSubmit={handleRename}
        onClose={() => setShowRenameModal(false)}
        inputType="text"
        initialValue={selectedFiles[0]?.name}
      />
      <InputModal
        title={'Setting Replication factor for: ' + selectedFile}
        inputLabel={t('Replication factor:')}
        submitText={t('Submit')}
        showModal={showReplicationModal}
        onSubmit={handleReplication}
        onClose={() => setShowReplicationModal(false)}
        inputType="number"
        initialValue={selectedFiles[0]?.replication}
      />
      <FileChooserModal
        onClose={() => setShowCopyModal(false)}
        onSubmit={handleCopy}
        showModal={showCopyModal}
        title="Copy to"
        sourcePath={currentPath}
        submitText={t('Copy')}
      />
      <FileChooserModal
        onClose={() => setShowMoveModal(false)}
        onSubmit={handleMove}
        showModal={showMoveModal}
        title="Move to"
        sourcePath={currentPath}
        submitText={t('Move')}
      />
    </>
  );
};

export default StorageBrowserActions;
