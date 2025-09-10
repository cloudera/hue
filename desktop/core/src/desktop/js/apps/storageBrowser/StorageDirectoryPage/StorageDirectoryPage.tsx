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

import React, { useMemo, useState, useCallback } from 'react';
import { Input, Tooltip } from 'antd';

import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';

import { i18nReact } from '../../../utils/i18nReact';
import useDebounce from '../../../utils/useDebounce';

import { LIST_DIRECTORY_API_URL } from '../api';
import {
  ListDirectory,
  FileStats,
  BrowserViewType,
  StorageDirectoryTableData,
  FileSystem
} from '../types';
import formatBytes from '../../../utils/formatBytes';
import { formatTimestamp } from '../../../utils/dateTimeUtils';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { DEFAULT_PAGE_SIZE, DEFAULT_POLLING_TIME } from '../../../utils/constants/storageBrowser';
import DragAndDrop from '../../../reactComponents/DragAndDrop/DragAndDrop';
import UUID from '../../../utils/string/UUID';
import { FileStatus } from '../../../utils/hooks/useFileUpload/types';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import StorageDirectoryActions from './StorageDirectoryActions/StorageDirectoryActions';
import PaginatedTable, {
  SortOrder,
  ColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import { getLastDirOrFileNameFromPath } from '../../../reactComponents/PathBrowser/PathBrowser.util';
import huePubSub from '../../../utils/huePubSub';
import { useHuePubSub } from '../../../utils/hooks/useHuePubSub/useHuePubSub';
import {
  FILE_UPLOAD_START_EVENT,
  FILE_UPLOAD_SUCCESS_EVENT
} from '../../../reactComponents/FileUploadQueue/event';
import { isFileSystemNonRoot } from '../utils/utils';

import './StorageDirectoryPage.scss';

interface StorageDirectoryPageProps {
  fileStats: FileStats;
  fileSystem: FileSystem;
  onFilePathChange: (path: string) => void;
  testId?: string;
  reloadTrashPath: () => void;
}

const defaultProps = {
  testId: 'hue-storage-browser__table'
};

const StorageDirectoryPage = ({
  fileStats,
  fileSystem,
  onFilePathChange,
  testId,
  reloadTrashPath
}: StorageDirectoryPageProps): JSX.Element => {
  const [selectedFiles, setSelectedFiles] = useState<StorageDirectoryTableData[]>([]);
  const [polling, setPolling] = useState<boolean>(false);

  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [sortByColumn, setSortByColumn] =
    useState<ColumnProps<StorageDirectoryTableData>['dataIndex']>();
  const [sortOrder, setSortOrder] = useState<SortOrder>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');

  const { t } = i18nReact.useTranslation();

  const {
    data: filesData,
    loading: listDirectoryLoading,
    error: listDirectoryError,
    reloadData: reloadFilesData
  } = useLoadData<ListDirectory>(LIST_DIRECTORY_API_URL, {
    params: {
      path: fileStats.path,
      pagesize: pageSize.toString(),
      pagenum: pageNumber.toString(),
      filter: searchTerm !== '' ? searchTerm : undefined,
      sortby: sortByColumn,
      descending: sortOrder !== null ? sortOrder === 'descend' : undefined
    },
    skip:
      fileStats.path === '' ||
      fileStats.path === undefined ||
      fileStats.type !== BrowserViewType.dir,
    onSuccess: () => setSelectedFiles([]),
    pollInterval: polling ? DEFAULT_POLLING_TIME : undefined
  });

  const tableData: StorageDirectoryTableData[] = useMemo(() => {
    if (!filesData?.files) {
      return [];
    }

    return filesData?.files?.map(file => ({
      name: getLastDirOrFileNameFromPath(file.path),
      size: file.type === BrowserViewType.file ? formatBytes(file.size) : '',
      user: file.user,
      group: file.group,
      permission: file.rwx,
      mtime: file?.mtime ? formatTimestamp(new Date(file.mtime * 1000)) : '-',
      type: file.type,
      path: file.path,
      replication: file?.replication
    }));
  }, [filesData]);

  const onRowClicked = (record: StorageDirectoryTableData) => {
    return {
      onClick: (event: React.MouseEvent) => {
        // Handle CTRL+click to open in new tab
        if (event.ctrlKey || event.metaKey) {
          const currentUrl = new URL(window.location.href);
          currentUrl.searchParams.set('path', record.path);
          window.open(currentUrl.toString(), '_blank');
          return;
        }

        // Normal click behavior
        if (selectedFiles.length === 0) {
          onFilePathChange(record.path);
          if (record.type === 'dir') {
            setPageNumber(1);
          }
        }
      }
    };
  };

  const handleSearch = useCallback(
    useDebounce(searchTerm => {
      setSearchTerm(encodeURIComponent(searchTerm));
    }),
    [setSearchTerm]
  );

  const onFilesDrop = (newFiles: File[]) => {
    const newUploadItems = newFiles.map(file => {
      return {
        file,
        filePath: fileStats.path,
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

  const errorConfig = [
    {
      enabled: !!listDirectoryError,
      message: t('An error occurred while fetching the data'),
      actionText: t('Retry'),
      onClick: reloadFilesData
    }
  ];

  const columnsConfig: ColumnProps<StorageDirectoryTableData>[] = [
    {
      title: t('Name'),
      dataIndex: 'name',
      key: 'name',
      sorter: (filesData?.files?.length ?? 0) > 1,
      width: '40%',
      render: (_, record) => (
        <Tooltip title={record.name} mouseEnterDelay={1.5}>
          <div className="hue-storage-browser-directory__name-column">
            <div className="hue-storage-browser-directory__name-column__icon">
              {record.type === BrowserViewType.dir ? (
                <FolderIcon height={18} width={18} />
              ) : (
                <FileIcon height={18} width={18} />
              )}
            </div>
            <div className="hue-storage-browser-directory__name-column__label">{record.name}</div>
          </div>
        </Tooltip>
      )
    },
    {
      title: t('Size'),
      dataIndex: 'size',
      key: 'size',
      width: '10%',
      sorter: (filesData?.files?.length ?? 0) > 1
    },
    {
      title: t('User'),
      dataIndex: 'user',
      key: 'user',
      width: '10%'
    },
    {
      title: t('Group'),
      dataIndex: 'group',
      key: 'group',
      width: '10%'
    },
    {
      title: t('Permission'),
      dataIndex: 'permission',
      key: 'permission',
      width: '10%'
    },
    {
      title: t('Last Updated'),
      dataIndex: 'mtime',
      key: 'mtime',
      width: '20%',
      sorter: (filesData?.files?.length ?? 0) > 1
    }
  ];

  return (
    <div className="hue-storage-browser-directory">
      <div className="hue-storage-browser-directory__actions-bar">
        <Input
          className="hue-storage-browser-directory__actions-bar__search"
          data-testid="hue-storage-browser-directory__actions-bar__search"
          placeholder={t('Search')}
          allowClear={true}
          onChange={event => handleSearch(event.target.value)}
          disabled={!tableData.length && !searchTerm.length}
        />
        <div className="hue-storage-browser-directory__actions-bar__actions">
          <StorageDirectoryActions
            fileStats={fileStats}
            fileSystem={fileSystem}
            selectedFiles={selectedFiles}
            onFilePathChange={onFilePathChange}
            onActionSuccess={() => {
              reloadFilesData();
              reloadTrashPath();
            }}
            onFilesDrop={onFilesDrop}
          />
        </div>
      </div>

      <DragAndDrop onDrop={onFilesDrop} disabled={!isFileSystemNonRoot(fileStats.path)}>
        <LoadingErrorWrapper errors={errorConfig}>
          <PaginatedTable<StorageDirectoryTableData>
            loading={listDirectoryLoading && !polling}
            data={tableData}
            columns={columnsConfig}
            rowKey={r => `${r.path}_${r.type}_${r.mtime}`}
            onRowClick={onRowClicked}
            onRowSelect={setSelectedFiles}
            sortByColumn={sortByColumn}
            setSortByColumn={setSortByColumn}
            sortOrder={sortOrder}
            setSortOrder={setSortOrder}
            locale={{
              emptyText: searchTerm.length ? t('No results found!') : t('Folder is empty')
            }}
            isDynamicHeight
            testId={testId}
            pagination={{
              pageSize,
              setPageSize,
              setPageNumber,
              pageStats: filesData?.page
            }}
          />
        </LoadingErrorWrapper>
      </DragAndDrop>
    </div>
  );
};

StorageDirectoryPage.defaultProps = defaultProps;
export default StorageDirectoryPage;
