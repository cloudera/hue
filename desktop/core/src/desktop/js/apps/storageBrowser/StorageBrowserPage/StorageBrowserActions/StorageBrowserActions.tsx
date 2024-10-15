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

import React, { useState } from 'react';
import { Dropdown } from 'antd';
import { MenuItemType } from 'antd/lib/menu/hooks/useItems';

import Button from 'cuix/dist/components/Button';
import DropDownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';
import InfoIcon from '@cloudera/cuix-core/icons/react/InfoIcon';
import CloseIcon from '@cloudera/cuix-core/icons/react/CloseIcon';
import DeleteIcon from '@cloudera/cuix-core/icons/react/DeleteIcon';
import DataMovementIcon from '@cloudera/cuix-core/icons/react/DataMovementIcon';
import CopyClipboardIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';
import DuplicateIcon from '@cloudera/cuix-core/icons/react/DuplicateIcon';
import DownloadIcon from '@cloudera/cuix-core/icons/react/DownloadIcon';

import { i18nReact } from '../../../../utils/i18nReact';
import { StorageBrowserTableData } from '../../../../reactComponents/FileChooser/types';
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
  rename,
  setReplication,
  move,
  copy,
  rmtree,
  download
} from '../../../../reactComponents/FileChooser/api';
import huePubSub from '../../../../utils/huePubSub';

import SummaryModal from '../../SummaryModal/SummaryModal';
import InputModal from '../../InputModal/InputModal';

import './StorageBrowserActions.scss';
import ConfirmationModal from '../../ConfirmationModal/ConfirmationModal';
import SetReplicationModal from '../../SetReplicationModal/SetReplicationModal';
import CopyMoveModal from '../../CopyMoveModal/CopyMoveModal';

interface StorageBrowserRowActionsProps {
  selectedFiles: StorageBrowserTableData[];
  onSuccessfulAction: () => void;
  setLoadingFiles: (value: boolean) => void;
  isTrashEnabled: boolean;
  isFsSuperuser: boolean;
  currentPath: string;
}
//TODO: maybe add current path to props

const StorageBrowserActions = ({
  selectedFiles,
  setLoadingFiles,
  onSuccessfulAction,
  isTrashEnabled,
  // isFsSuperuser,
  currentPath
}: StorageBrowserRowActionsProps): JSX.Element => {
  const [showSummaryModal, setShowSummaryModal] = useState<boolean>(false);
  const [showRenameModal, setShowRenameModal] = useState<boolean>(false);
  const [showMoveModal, setShowMoveModal] = useState<boolean>(false);
  const [showCopyModal, setShowCopyModal] = useState<boolean>(false);
  const [showReplicationModal, setShowReplicationModal] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [skipTrash, setSkipTrash] = useState<boolean>(false);
  const [showDeleteConfirmationModal, setShowDeleteConfirmationModal] = useState<boolean>(false);
  // const [showPurgeConfirmationModal, setShowPurgeConfirmationModal] = useState<boolean>(false);
  // const [showRestoreConfirmationModal, setShowRestoreConfirmationModal] = useState<boolean>(false);

  const { t } = i18nReact.useTranslation();

  const handleRename = (newName: string) => {
    setLoadingFiles(true);
    rename(selectedFile, newName)
      .then(() => {
        onSuccessfulAction();
      })
      .catch(error => {
        huePubSub.publish('hue.error', error);
        setShowRenameModal(false);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  };

  const handleReplication = (replicationFactor: number) => {
    setLoadingFiles(true);
    setReplication(selectedFile, replicationFactor)
      .then(() => {
        onSuccessfulAction();
      })
      .catch(error => {
        huePubSub.publish('hue.error', error);
        setShowReplicationModal(false);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  };

  const handleCopy = (dest_path: string) => {
    setLoadingFiles(true);
    copy(selectedFile, dest_path)
      .then(() => {
        onSuccessfulAction();
      })
      .catch(error => {
        huePubSub.publish('hue.error', error);
        setShowCopyModal(false);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  };

  const handleMove = (dest_path: string) => {
    setLoadingFiles(true);
    move(selectedFile, dest_path)
      .then(() => {
        onSuccessfulAction();
      })
      .catch(error => {
        huePubSub.publish('hue.error', error);
        setShowMoveModal(false);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  };

  const handleDelete = () => {
    setLoadingFiles(true);
    rmtree(selectedFile, true)
      .then(() => {
        onSuccessfulAction();
      })
      .catch(error => {
        huePubSub.publish('hue.error', error);
        setShowDeleteConfirmationModal(false);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  };

  const handleDownload = () => {
    download(selectedFiles[0].path)
      .then(responseSummary => {
        // eslint-disable-next-line no-restricted-syntax
        console.log(responseSummary);
      })
      .catch(error => {
        huePubSub.publish('hue.error', error);
      })
      .finally(() => {});
    huePubSub.publish('hue.global.info', { message: t('Downloading your file, Please wait...') });
  };

  const isSummaryEnabled = () => {
    if (selectedFiles.length !== 1) {
      return false;
    }
    const selectedFile = selectedFiles[0];
    return (isHDFS(selectedFile.path) || isOFS(selectedFile.path)) && selectedFile.type === 'file';
  };

  const isRenameEnabled = () => {
    if (selectedFiles.length !== 1) {
      return false;
    }
    const selectedFilePath = selectedFiles[0].path;
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

  const isMoveToTrashEnabled = () => {
    return selectedFiles.length > 0;
  };
  // trashselected -> onclick
  const isDeleteForeverEnabled = () => {
    return selectedFiles.length > 0;
  };
  // deleteselected -> onclick
  //TODO: combine rename, copy and move conditions
  const isMoveEnabled = () => {
    if (selectedFiles.length > 0) {
      const selectedFilePath = selectedFiles[0].path;
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
    }
    return false;
  };

  const isCopyEnabled = () => {
    if (selectedFiles.length > 0) {
      const selectedFilePath = selectedFiles[0].path;
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
    }
    return false;
  };

  const isReplicationEnabled = () => {
    if (selectedFiles.length !== 1) {
      return false;
    }
    const selectedFile = selectedFiles[0];
    return isHDFS(selectedFile.path) && selectedFile.type === 'file';
  };

  const isDownloadEnabled = () => {
    if (selectedFiles.length !== 1 || selectedFiles[0].type !== 'file') {
      return false;
    }
    return true;
  };
  // const isPermissionsEnabled = () => {};
  // const isSetReplicationEnabled = () => {};
  // const isChangePermissionsEnabled = () => {};
  // const isChangeGroupOrOwnerEnabled = () => {};
  // const isCompressEnabled
  // const isExtractEnabled
  // const isReplicationEnabled
  // const isTrashEnabled
  // const isDeleteEnabled
  // const isInTrash
  // const isInRestorableTrash

  const getActions = () => {
    const actions: MenuItemType[] = [];
    if (selectedFiles && selectedFiles.length > 0 && !inTrash(selectedFiles[0].path)) {
      if (isSummaryEnabled()) {
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
      if (isRenameEnabled()) {
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
      if (isDownloadEnabled()) {
        actions.push({
          key: 'download',
          icon: <DownloadIcon />,
          label: t('Download'),
          onClick: () => {
            setSelectedFile(selectedFiles[0].path);
            handleDownload();
          }
        });
      }
      if (isMoveEnabled()) {
        actions.push({
          key: 'move',
          icon: <DataMovementIcon />,
          label: t('Move'),
          onClick: () => {
            setSelectedFile(selectedFiles[0].path);
            setShowMoveModal(true);
          }
        });
      }
      if (isCopyEnabled()) {
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
      if (isReplicationEnabled()) {
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
      if (isTrashEnabled && isMoveToTrashEnabled()) {
        actions.push({
          key: 'moveToTrash',
          icon: <CloseIcon />,
          label: t('Move to Trash'),
          danger: true,
          onClick: () => {
            setSkipTrash(false);
            setSelectedFile(selectedFiles[0].path);
            setShowDeleteConfirmationModal(true);
          }
        });
      }
      if (isDeleteForeverEnabled()) {
        actions.push({
          key: 'deleteForever',
          icon: <DeleteIcon />,
          label: t('Delete Forever'),
          danger: true,
          onClick: () => {
            setSkipTrash(true);
            setSelectedFile(selectedFiles[0].path);
            setShowDeleteConfirmationModal(true);
          }
        });
      }
    }
    return actions;
  };

  const getDeleteConfirmationModalBody = (): JSX.Element => {
    let body: JSX.Element = <div></div>;
    //TODO: run only if modal is open
    if (selectedFiles.length > 0) {
      // eslint-disable-next-line no-restricted-syntax
      // console.log(selectedFiles);
      if (
        (isS3(selectedFiles[0].path) && isS3Root(selectedFiles[0].path)) ||
        (isGS(selectedFiles[0].path) && isGSRoot(selectedFiles[0].path))
      ) {
        body = (
          <div>
            <p>Are you sure you want to delete these buckets?</p>
            <p className="muted">
              Deleting a bucket will delete all of its contents and release the bucket name to be
              reserved by others.
            </p>
          </div>
        );
      }
      if (
        !(
          isS3(selectedFiles[0].path) &&
          isS3Root(selectedFiles[0].path) &&
          isGS(selectedFiles[0].path) &&
          isGSRoot(selectedFiles[0].path)
        )
      ) {
        if (!skipTrash) {
          body = (
            <div>
              <p>Are you sure you want to delete these files?</p>
              <ul style={{ marginLeft: '25px' }}>
                {selectedFiles.map((file, i) => {
                  if (i < 10) {
                    return <li key={file.path}>{file.name}</li>;
                  }
                })}
              </ul>
              {selectedFiles.length > 10 ? <div>and others</div> : <div />}
            </div>
          );
        } else {
          body = (
            <div>
              <p>Are you sure you want to permanently delete these files?</p>
              <ul style={{ marginLeft: '25px' }}>
                {selectedFiles.map((file, i) => {
                  if (i < 10) {
                    return <li key={file.path}>{file.name}</li>;
                  }
                })}
              </ul>
              {selectedFiles.length > 10 ? <div>and others</div> : <div />}
            </div>
          );
        }
      }
    }
    return body;
  };

  // const getPurgeConfirmationModalBody = (): JSX.Element => {
  //   const body: JSX.Element = (
  //     <div>
  //       <p>Are you sure you want to permanently delete all your trash?</p>
  //     </div>
  //   );
  //   return body;
  // };

  // const getRestoreConfirmationModalBody = (): JSX.Element => {
  //   const body: JSX.Element = (
  //     <div>
  //       <p>Are you sure you want to restore these files?</p>
  //     </div>
  //   );
  //   return body;
  // };

  return (
    <>
      <Dropdown
        overlayClassName="hue-storage-browser__table-actions-dropdown"
        menu={{
          items: getActions(),
          className: 'hue-storage-browser__table-actions-menu'
        }}
        trigger={['click', 'hover']}
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
      />
      <ConfirmationModal
        onClose={() => setShowDeleteConfirmationModal(false)}
        onSubmit={handleDelete}
        showModal={showDeleteConfirmationModal}
        title="Confirm Delete"
        modalBody={getDeleteConfirmationModalBody()}
        okText={t('Yes')}
        cancelText={t('No')}
      />
      {/* <ConfirmationModal
        onClose={() => setShowPurgeConfirmationModal(false)}
        onSubmit={() => {}}
        showModal={showPurgeConfirmationModal}
        title="Confirm empty trash"
        modalBody={getPurgeConfirmationModalBody()}
        okText={t('Delete all')}
        cancelText={t('Cancel')}
      />
      <ConfirmationModal
        onClose={() => setShowRestoreConfirmationModal(false)}
        onSubmit={() => {}}
        showModal={showRestoreConfirmationModal}
        title="Confirm Restore"
        modalBody={getRestoreConfirmationModalBody()}
        okText={t('Yes')}
        cancelText={t('No')}
      /> */}
      {/* TODO: edit replication factor */}
      <SetReplicationModal
        onClose={() => setShowReplicationModal(false)}
        onSubmit={handleReplication}
        showModal={showReplicationModal}
        title={'Setting Replication factor for: ' + selectedFile}
        currentReplicationFactor={2}
      />
      <CopyMoveModal
        onClose={() => setShowCopyModal(false)}
        onSubmit={handleCopy}
        showModal={showCopyModal}
        title="Copy to"
        sourcePath={currentPath}
      />
      <CopyMoveModal
        onClose={() => setShowMoveModal(false)}
        onSubmit={handleMove}
        showModal={showMoveModal}
        title="Move to"
        sourcePath={currentPath}
      />
    </>
  );
};

export default StorageBrowserActions;
