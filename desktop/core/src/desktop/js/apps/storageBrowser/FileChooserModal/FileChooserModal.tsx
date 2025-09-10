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

import React, { useCallback, useMemo, useRef, useState } from 'react';
import Modal from 'cuix/dist/components/Modal';
import { Input, InputRef, Tooltip } from 'antd';
import { ColumnProps } from 'cuix/dist/components/Table';
import classNames from 'classnames';

import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';

import { i18nReact } from '../../../utils/i18nReact';
import useDebounce from '../../../utils/useDebounce';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import huePubSub from '../../../utils/huePubSub';
import { useHuePubSub } from '../../../utils/hooks/useHuePubSub/useHuePubSub';
import { FileStatus } from '../../../utils/hooks/useFileUpload/types';
import UUID from '../../../utils/string/UUID';
import { DEFAULT_POLLING_TIME } from '../../../utils/constants/storageBrowser';

import { BrowserViewType, ListDirectory } from '../types';
import { LIST_DIRECTORY_API_URL, CREATE_DIRECTORY_API_URL } from '../api';

import PathBrowser from '../../../reactComponents/PathBrowser/PathBrowser';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import DragAndDrop from '../../../reactComponents/DragAndDrop/DragAndDrop';
import BottomSlidePanel from '../../../reactComponents/BottomSlidePanel/BottomSlidePanel';
import PaginatedTable from '../../../reactComponents/PaginatedTable/PaginatedTable';
import {
  FILE_UPLOAD_START_EVENT,
  FILE_UPLOAD_SUCCESS_EVENT
} from '../../../reactComponents/FileUploadQueue/event';

import './FileChooserModal.scss';

interface FileChooserModalProps {
  onClose: () => void;
  onSubmit: (destinationPath: string) => Promise<void>;
  showModal: boolean;
  title: string;
  sourcePath: string;
  submitText?: string;
  cancelText?: string;
  isFileSelectionAllowed?: boolean;
  isUploadEnabled?: boolean;
}

interface FileChooserTableData {
  name: string;
  path: string;
  type: string;
}

const FileChooserModal = ({
  showModal,
  onClose,
  onSubmit,
  title,
  sourcePath,
  isFileSelectionAllowed = false,
  isUploadEnabled = false,
  ...i18n
}: FileChooserModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const { cancelText = t('Cancel'), submitText = t('Submit') } = i18n;
  const [destPath, setDestPath] = useState<string>(sourcePath);
  const [submitLoading, setSubmitLoading] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [showCreateFolderModal, setShowCreateFolderModal] = useState<boolean>(false);
  const [polling, setPolling] = useState<boolean>(false);
  const uploadRef = useRef<HTMLInputElement>(null);
  const createFolderInputRef = useRef<InputRef>(null);
  const [createFolderValue, setCreateFolderValue] = useState<string>('');

  const {
    data: filesData,
    loading,
    error,
    reloadData
  } = useLoadData<ListDirectory>(LIST_DIRECTORY_API_URL, {
    params: {
      path: destPath,
      pagesize: '1000',
      filter: searchTerm
    },
    skip: destPath === '' || destPath === undefined || !showModal,
    pollInterval: polling ? DEFAULT_POLLING_TIME : undefined
  });

  const tableData: FileChooserTableData[] = useMemo(() => {
    if (!filesData?.files) {
      return [];
    }

    return filesData?.files?.map(file => ({
      name: file.path.split('/').pop() ?? '',
      path: file.path,
      type: file.type
    }));
  }, [filesData, loading, error]);

  const handleSearch = useCallback(
    useDebounce(searchTerm => {
      setSearchTerm(encodeURIComponent(searchTerm));
    }),
    [setSearchTerm]
  );

  const getColumns = (file: FileChooserTableData) => {
    const columns: ColumnProps<FileChooserTableData>[] = [];
    for (const key of Object.keys(file)) {
      const column: ColumnProps<FileChooserTableData> = {
        dataIndex: key,
        key: `${key}`
      };
      if (key === 'name') {
        column.render = (_, record: FileChooserTableData) => (
          <Tooltip title={record.name} mouseEnterDelay={1.5}>
            <span className="hue-filechooser-modal__table-cell-icon">
              {record.type === BrowserViewType.dir ? <FolderIcon /> : <FileIcon />}
            </span>
            <span
              className="hue-filechooser-modal__table-cell-name"
              data-testid="hue-filechooser-modal__table-cell-name"
            >
              {record.name}
            </span>
          </Tooltip>
        );
      }
      columns.push(column);
    }
    return columns.filter(col => col.dataIndex !== 'type' && col.dataIndex !== 'path');
  };

  const onRowClicked = (record: FileChooserTableData) => {
    return {
      onClick: () => {
        if (record.type === BrowserViewType.dir) {
          setDestPath(record.path);
        }
        if (isFileSelectionAllowed && record.type === BrowserViewType.file) {
          onSubmit(record.path);
          onClose();
        }
      }
    };
  };

  const onFilesDrop = (newFiles: File[]) => {
    const newUploadItems = newFiles.map(file => {
      return {
        file,
        filePath: destPath,
        uuid: UUID(),
        status: FileStatus.Pending
      };
    });
    setPolling(true);
    huePubSub.publish(FILE_UPLOAD_START_EVENT, {
      files: newUploadItems
    });
  };

  useHuePubSub({
    topic: FILE_UPLOAD_SUCCESS_EVENT,
    callback: () => {
      setPolling(false);
    }
  });

  const handleUploadClick = () => {
    if (!uploadRef || !uploadRef.current) {
      return;
    }
    uploadRef.current.click();
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files as ArrayLike<File>);
    onFilesDrop(files);
  };

  const {
    save: createFolder,
    loading: createFolderLoading,
    error: createFolderError
  } = useSaveData(CREATE_DIRECTORY_API_URL, {
    options: { qsEncodeData: true } // TODO: Remove once API supports RAW JSON payload
  });

  const handleCreate = () => {
    createFolder(
      { path: destPath, name: createFolderValue },
      {
        onSuccess: () => {
          setShowCreateFolderModal(false);
          setDestPath(prev => `${prev}/${createFolderValue}`);
        }
      }
    );
  };

  const locale = {
    emptyText: t('Folder is empty')
  };

  const handleOk = async () => {
    setSubmitLoading(true);
    await onSubmit(destPath);
    setSubmitLoading(false);
    onClose();
  };

  const errorConfig = [
    {
      enabled: !!error,
      message: t('An error occurred while fetching the filesystem'),
      action: t('Retry'),
      onClick: reloadData
    }
  ];

  const createFolderErrorConfig = [
    {
      enabled: !!createFolderError,
      message: createFolderError
    }
  ];

  const TableContent = (
    <LoadingErrorWrapper errors={errorConfig}>
      <PaginatedTable<FileChooserTableData>
        loading={loading && !polling}
        data={tableData}
        isDynamicHeight
        rowKey={r => `${r.path}__${r.type}__${r.name}`}
        locale={locale}
        columns={getColumns(tableData[0] ?? {})}
        rowClassName={record =>
          record.type === BrowserViewType.file && !isFileSelectionAllowed
            ? classNames('hue-filechooser-modal__table-row', 'disabled-row')
            : 'hue-filechooser-modal__table-row'
        }
        onRowClick={onRowClicked}
        showHeader={false}
      />
    </LoadingErrorWrapper>
  );

  return (
    <>
      {showModal && (
        <Modal
          open={showModal}
          title={title}
          className="hue-filechooser-modal cuix antd"
          onOk={isUploadEnabled ? handleUploadClick : handleOk}
          okText={isUploadEnabled ? t('Upload file') : submitText}
          okButtonProps={
            !isUploadEnabled ? { disabled: sourcePath === destPath, loading: submitLoading } : {}
          }
          secondaryButtonText={t('Create folder')}
          onSecondary={() => setShowCreateFolderModal(true)}
          cancelText={cancelText}
          onCancel={onClose}
        >
          <div className="hue-filechooser-modal__body">
            <div className="hue-filechooser-modal__path-browser-panel">
              <PathBrowser filePath={destPath} onFilepathChange={setDestPath} showIcon={false} />
            </div>
            <Input
              className="hue-filechooser-modal__search"
              placeholder={t('Search')}
              allowClear={true}
              onChange={event => {
                handleSearch(event.target.value);
              }}
            />
            {isUploadEnabled ? (
              <DragAndDrop onDrop={onFilesDrop}>{TableContent}</DragAndDrop>
            ) : (
              TableContent
            )}
          </div>
          <input
            ref={uploadRef}
            type="file"
            className="hue-importer__source-selector-option-upload"
            onChange={handleFileUpload}
          />
          {showCreateFolderModal && (
            <BottomSlidePanel
              isOpen={showCreateFolderModal}
              title={t('Create Folder')}
              cancelText="Cancel"
              primaryText={t('Create')}
              onClose={() => {
                setShowCreateFolderModal(false);
                setCreateFolderValue('');
              }}
              onPrimaryClick={handleCreate}
            >
              {/* TODO: Refactor CreateAndUpload to reuse */}
              <LoadingErrorWrapper errors={createFolderErrorConfig}>
                <Input
                  defaultValue={createFolderValue}
                  disabled={createFolderLoading}
                  onPressEnter={() => handleCreate()}
                  ref={createFolderInputRef}
                  onChange={e => {
                    setCreateFolderValue(e.target.value);
                  }}
                />
              </LoadingErrorWrapper>
            </BottomSlidePanel>
          )}
        </Modal>
      )}
    </>
  );
};

export default FileChooserModal;
