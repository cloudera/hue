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
import { ColumnProps } from 'antd/lib/table';
import { Input, Tooltip } from 'antd';

import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';
import SortAscending from '@cloudera/cuix-core/icons/react/SortAscendingIcon';
import SortDescending from '@cloudera/cuix-core/icons/react/SortDescendingIcon';

import Table from 'cuix/dist/components/Table';

import { i18nReact } from '../../../utils/i18nReact';
import useDebounce from '../../../utils/useDebounce';

import { LIST_DIRECTORY_API_URL } from '../api';
import {
  SortOrder,
  ListDirectory,
  FileStats,
  BrowserViewType,
  StorageDirectoryTableData,
  FileSystem
} from '../types';
import Pagination from '../../../reactComponents/Pagination/Pagination';
import formatBytes from '../../../utils/formatBytes';

import './StorageDirectoryPage.scss';
import { formatTimestamp } from '../../../utils/dateTimeUtils';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import {
  DEFAULT_PAGE_SIZE,
  DEFAULT_POLLING_TIME,
  FileUploadStatus
} from '../../../utils/constants/storageBrowser';
import DragAndDrop from '../../../reactComponents/DragAndDrop/DragAndDrop';
import UUID from '../../../utils/string/UUID';
import { UploadItem } from '../../../utils/hooks/useFileUpload/util';
import FileUploadQueue from '../../../reactComponents/FileUploadQueue/FileUploadQueue';
import { useWindowSize } from '../../../utils/hooks/useWindowSize/useWindowSize';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import StorageDirectoryActions from './StorageDirectoryActions/StorageDirectoryActions';

interface StorageDirectoryPageProps {
  fileStats: FileStats;
  fileSystem: FileSystem;
  onFilePathChange: (path: string) => void;
  className?: string;
  rowClassName?: string;
  testId?: string;
  reloadTrashPath: () => void;
}

const defaultProps = {
  className: 'hue-storage-browser__table',
  rowClassName: 'hue-storage-browser__table-row',
  testId: 'hue-storage-browser__table'
};

const StorageDirectoryPage = ({
  fileStats,
  fileSystem,
  onFilePathChange,
  className,
  rowClassName,
  testId,
  reloadTrashPath,
  ...restProps
}: StorageDirectoryPageProps): JSX.Element => {
  const [loadingFiles, setLoadingFiles] = useState<boolean>(false);
  const [selectedFiles, setSelectedFiles] = useState<StorageDirectoryTableData[]>([]);
  const [filesToUpload, setFilesToUpload] = useState<UploadItem[]>([]);
  const [polling, setPolling] = useState<boolean>(false);

  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [sortByColumn, setSortByColumn] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<SortOrder>(SortOrder.NONE);
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
      filter: searchTerm,
      sortby: sortByColumn,
      descending: sortOrder === SortOrder.DSC ? 'true' : 'false'
    },
    skip:
      fileStats.path === '' ||
      fileStats.path === undefined ||
      fileStats.type !== BrowserViewType.dir,
    onSuccess: () => {
      setSelectedFiles([]);
    },
    pollInterval: polling ? DEFAULT_POLLING_TIME : undefined
  });

  const tableData: StorageDirectoryTableData[] = useMemo(() => {
    if (!filesData?.files) {
      return [];
    }

    return filesData?.files?.map(file => ({
      name: file.path.split('/').pop() ?? '',
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

  const onColumnTitleClicked = (columnClicked: string) => {
    if (columnClicked === sortByColumn) {
      if (sortOrder === SortOrder.NONE) {
        setSortOrder(SortOrder.ASC);
      } else if (sortOrder === SortOrder.ASC) {
        setSortOrder(SortOrder.DSC);
      } else {
        setSortOrder(SortOrder.NONE);
      }
    } else {
      setSortByColumn(columnClicked);
      setSortOrder(SortOrder.ASC);
    }
  };

  const getColumns = (file: StorageDirectoryTableData) => {
    const columns: ColumnProps<StorageDirectoryTableData>[] = [];
    for (const key of Object.keys(file)) {
      const column: ColumnProps<StorageDirectoryTableData> = {
        dataIndex: key,
        title: (
          <div
            className="hue-storage-browser__table-column-header"
            onClick={() => onColumnTitleClicked(key)}
          >
            <div className="hue-storage-browser__table-column-title">
              {key === 'mtime' ? t('Last Updated') : t(key)}
            </div>
            {key === sortByColumn ? (
              sortOrder === SortOrder.DSC ? (
                <SortDescending />
              ) : sortOrder === SortOrder.ASC ? (
                <SortAscending />
              ) : null
            ) : null}
          </div>
        ),
        key: `${key}`
      };
      if (key === 'name') {
        column.width = '40%';
        column.render = (_, record: StorageDirectoryTableData) => (
          <Tooltip title={record.name} mouseEnterDelay={1.5}>
            <span className="hue-storage-browser__table-cell-icon">
              {record.type === 'dir' ? <FolderIcon /> : <FileIcon />}
            </span>
            <span className="hue-storage-browser__table-cell-name">{record.name}</span>
          </Tooltip>
        );
      } else if (key === 'mtime') {
        column.width = '20%';
      } else if (key === 'permission') {
        column.width = '12%';
      }
      columns.push(column);
    }
    return columns.filter(
      col => col.dataIndex !== 'type' && col.dataIndex !== 'path' && col.dataIndex !== 'replication'
    );
  };

  const onRowClicked = (record: StorageDirectoryTableData) => {
    return {
      onClick: () => {
        if (selectedFiles.length === 0) {
          onFilePathChange(record.path);
          if (record.type === 'dir') {
            setPageNumber(1);
          }
        }
      }
    };
  };

  const rowSelection = {
    onChange: (_: React.Key[], selectedRows: StorageDirectoryTableData[]) => {
      setSelectedFiles(selectedRows);
    }
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
        status: FileUploadStatus.Pending
      };
    });
    setPolling(true);
    setFilesToUpload(prevFiles => [...prevFiles, ...newUploadItems]);
  };

  const [tableRef, rect] = useWindowSize();
  // 40px for table header, 50px for pagination
  const tableBodyHeight = Math.max(rect.height - 90, 100);

  const locale = {
    emptyText: t('Folder is empty')
  };

  const errorConfig = [
    {
      enabled: !!listDirectoryError,
      message: t('An error occurred while fetching the data'),
      action: t('Retry'),
      onClick: reloadFilesData
    }
  ];

  return (
    <div className="hue-storage-browser-directory">
      <div className="hue-storage-browser-directory__actions-bar">
        <Input
          className="hue-storage-browser-directory__actions-bar__search"
          placeholder={t('Search')}
          allowClear={true}
          onChange={event => {
            handleSearch(event.target.value);
          }}
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
            setLoadingFiles={setLoadingFiles}
            onFilesDrop={onFilesDrop}
          />
        </div>
      </div>

      <div ref={tableRef} className="hue-storage-browser-directory__table-container">
        <DragAndDrop onDrop={onFilesDrop}>
          <LoadingErrorWrapper
            loading={(loadingFiles || listDirectoryLoading) && !polling}
            errors={errorConfig}
          >
            <Table
              className={className}
              columns={getColumns(tableData[0] ?? {})}
              dataSource={tableData}
              onRow={onRowClicked}
              pagination={false}
              rowClassName={rowClassName}
              rowKey={r => `${r.path}_${r.type}_${r.mtime}`}
              rowSelection={{
                hideSelectAll: !tableData.length,
                columnWidth: 36,
                type: 'checkbox',
                ...rowSelection
              }}
              scroll={{ y: tableBodyHeight }}
              data-testid={`${testId}`}
              locale={locale}
              {...restProps}
            />

            {filesData?.page && filesData?.page?.total_pages > 0 && (
              <Pagination
                setPageSize={setPageSize}
                pageSize={pageSize}
                setPageNumber={setPageNumber}
                pageStats={filesData?.page}
              />
            )}
          </LoadingErrorWrapper>
        </DragAndDrop>
      </div>
      {filesToUpload.length > 0 && (
        <FileUploadQueue
          filesQueue={filesToUpload}
          onClose={() => setFilesToUpload([])}
          onComplete={() => {
            reloadFilesData();
            setPolling(false);
          }}
        />
      )}
    </div>
  );
};

StorageDirectoryPage.defaultProps = defaultProps;
export default StorageDirectoryPage;
