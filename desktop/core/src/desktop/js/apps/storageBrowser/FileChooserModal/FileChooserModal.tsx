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

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Modal from 'cuix/dist/components/Modal';
import { Input, Tooltip } from 'antd';
import Table, { ColumnProps } from 'cuix/dist/components/Table';
import classNames from 'classnames';

import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';

import { i18nReact } from '../../../utils/i18nReact';
import useDebounce from '../../../utils/useDebounce';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';

import { BrowserViewType, ListDirectory } from '../types';
import { LIST_DIRECTORY_API_URL, CREATE_DIRECTORY_API_URL } from '../api';

import PathBrowser from '../../../reactComponents/PathBrowser/PathBrowser';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';

import './FileChooserModal.scss';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import huePubSub from '../../../utils/huePubSub';
import DragAndDrop from '../../../reactComponents/DragAndDrop/DragAndDrop';
import InputModal from '../../../reactComponents/InputModal/InputModal';
import { FileStatus, RegularFile } from '../../../utils/hooks/useFileUpload/types';
import FileUploadQueue from '../../../reactComponents/FileUploadQueue/FileUploadQueue';
import UUID from '../../../utils/string/UUID';
import { DEFAULT_POLLING_TIME } from '../../../utils/constants/storageBrowser';

interface FileChooserModalProps {
  onClose: () => void;
  onSubmit: (destination_path: string) => Promise<void>;
  showModal: boolean;
  title: string;
  sourcePath: string;
  submitText?: string;
  cancelText?: string;
  isImport?: boolean;
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
  isImport,
  ...i18n
}: FileChooserModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const { cancelText = t('Cancel'), submitText = t('Submit') } = i18n;
  const [destPath, setDestPath] = useState<string>(sourcePath);
  const [submitLoading, setSubmitLoading] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [showUploadModal, setShowUploadModal] = useState<boolean>(false);
  const [showCreateFolderModal, setShowCreateFolderModal] = useState<boolean>(false);
  const [polling, setPolling] = useState<boolean>(false);
  const [filesToUpload, setFilesToUpload] = useState<RegularFile[]>([]);

  useEffect(() => {
    if (showModal) {
      setDestPath(sourcePath);
    }
  }, [sourcePath]);

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

  const errorConfig = [
    {
      enabled: !!error,
      message: t('An error occurred while fetching the filesystem'),
      action: t('Retry'),
      onClick: reloadData
    }
  ];

  const tableData: FileChooserTableData[] = useMemo(() => {
    if (loading || error || !filesData?.files) {
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
            <span className="hue-filechooser-modal__table-cell-name">{record.name}</span>
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
        if (isImport && record.type === BrowserViewType.file) {
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
    setFilesToUpload(prevFiles => [...prevFiles, ...newUploadItems]);
  };

  const onUpload = (files: File[]) => {
    setShowUploadModal(false);
    onFilesDrop(files);
  };

  const { save: createFolder, loading: createFolderLoading } = useSaveData(
    CREATE_DIRECTORY_API_URL,
    {
      postOptions: { qsEncodeData: true } // TODO: Remove once API supports RAW JSON payload
    }
  );

  const handleCreate = (name: string | number) => {
    createFolder(
      { path: destPath, name: name },
      {
        onSuccess: () => {
          setShowCreateFolderModal(false);
          setDestPath(prev => `${prev}/${name}`);
        },
        onError: error => {
          huePubSub.publish('hue.error', error);
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

  return (
    <Modal
      open={showModal}
      title={title}
      className="hue-filechooser-modal cuix antd"
      onOk={isImport ? () => setShowUploadModal(true) : handleOk}
      okText={isImport ? t('Upload file') : submitText}
      okButtonProps={!isImport ? { disabled: sourcePath === destPath, loading: submitLoading } : {}}
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
        <LoadingErrorWrapper loading={loading && !polling} errors={errorConfig}>
          <Table
            className="hue-filechooser-modal__table"
            dataSource={tableData}
            pagination={false}
            columns={getColumns(tableData[0] ?? {})}
            rowKey={r => `${r.path}__${r.type}__${r.name}`}
            scroll={{ y: '250px' }}
            rowClassName={record =>
              record.type === BrowserViewType.file && !isImport
                ? classNames('hue-filechooser-modal__table-row', 'disabled-row')
                : 'hue-filechooser-modal__table-row'
            }
            onRow={onRowClicked}
            locale={locale}
            showHeader={false}
          />
        </LoadingErrorWrapper>
      </div>
      <Modal
        onCancel={() => setShowUploadModal(false)}
        className="hue-file-upload-modal cuix antd"
        open={showUploadModal}
        title={t('Upload a File')}
        destroyOnClose
      >
        <DragAndDrop onDrop={onUpload} />
      </Modal>
      {filesToUpload.length > 0 && (
        <FileUploadQueue
          filesQueue={filesToUpload}
          onClose={() => setFilesToUpload([])}
          onComplete={() => {
            reloadData();
            setPolling(false);
          }}
        />
      )}
      <InputModal
        showModal={showCreateFolderModal}
        title={t('Create Folder')}
        inputLabel={t('Folder name')}
        submitText={t('Create')}
        onSubmit={handleCreate}
        onClose={() => setShowCreateFolderModal(false)}
        loading={createFolderLoading}
      />
    </Modal>
  );
};

export default FileChooserModal;
