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

import React, { useMemo, useState, useCallback, useEffect } from 'react';
import { ColumnProps } from 'antd/lib/table';
import { Input, Tooltip } from 'antd';

import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import FileIcon from '@cloudera/cuix-core/icons/react/DocumentationIcon';
import SortAscending from '@cloudera/cuix-core/icons/react/SortAscendingIcon';
import SortDescending from '@cloudera/cuix-core/icons/react/SortDescendingIcon';

import Table from 'cuix/dist/components/Table';

import { i18nReact } from '../../../utils/i18nReact';
import useDebounce from '../../../utils/useDebounce';

import { LIST_DIRECTORY_API_URL } from '../../../reactComponents/FileChooser/api';
import {
  SortOrder,
  ListDirectory,
  FileStats,
  BrowserViewType,
  StorageDirectoryTableData
} from '../../../reactComponents/FileChooser/types';
import Pagination from '../../../reactComponents/Pagination/Pagination';
import StorageBrowserActions from './StorageBrowserActions/StorageBrowserActions';
import formatBytes from '../../../utils/formatBytes';

import './StorageDirectoryPage.scss';
import { formatTimestamp } from '../../../utils/dateTimeUtils';
import useLoadData from '../../../utils/hooks/useLoadData';
import { DEFAULT_PAGE_SIZE, FileUploadStatus } from '../../../utils/constants/storageBrowser';
import CreateAndUploadAction from './CreateAndUploadAction/CreateAndUploadAction';
import DragAndDrop from '../../../reactComponents/DragAndDrop/DragAndDrop';
import UUID from '../../../utils/string/UUID';
import { UploadItem } from '../../../utils/hooks/useFileUpload/util';
import FileUploadQueue from '../../../reactComponents/FileUploadQueue/FileUploadQueue';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';

interface StorageDirectoryPageProps {
  fileStats: FileStats;
  onFilePathChange: (path: string) => void;
  className?: string;
  rowClassName?: string;
  testId?: string;
}

const defaultProps = {
  className: 'hue-storage-browser__table',
  rowClassName: 'hue-storage-browser__table-row',
  testId: 'hue-storage-browser__table'
};

const StorageDirectoryPage = ({
  fileStats,
  onFilePathChange,
  className,
  rowClassName,
  testId,
  ...restProps
}: StorageDirectoryPageProps): JSX.Element => {
  const [loadingFiles, setLoadingFiles] = useState<boolean>(false);
  const [tableHeight, setTableHeight] = useState<number>(100);
  const [selectedFiles, setSelectedFiles] = useState<StorageDirectoryTableData[]>([]);
  const [filesToUpload, setFilesToUpload] = useState<UploadItem[]>([]);

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
    reloadData
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
    }
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

  //pagination related functions handled by parent
  const onPreviousPageButtonClicked = (previousPageNumber: number) => {
    //If previous page does not exists api returns 0
    setPageNumber(previousPageNumber === 0 ? 1 : previousPageNumber);
  };

  const onNextPageButtonClicked = (nextPageNumber: number, numPages: number) => {
    //If next page does not exists api returns 0
    setPageNumber(nextPageNumber === 0 ? numPages : nextPageNumber);
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
    setFilesToUpload(prevFiles => [...prevFiles, ...newUploadItems]);
  };

  useEffect(() => {
    //TODO: handle table resize
    const calculateTableHeight = () => {
      const windowHeight = window.innerHeight;
      // TODO: move 450 to dynamic based on  table header height, tab nav and some header.
      const tableHeightFix = windowHeight - 450;
      return tableHeightFix;
    };

    const handleWindowResize = () => {
      const tableHeight = calculateTableHeight();
      setTableHeight(tableHeight);
    };

    handleWindowResize(); // Calculate initial scroll height

    window.addEventListener('resize', handleWindowResize);

    return () => {
      window.removeEventListener('resize', handleWindowResize);
    };
  }, []);

  const locale = {
    emptyText: t('Folder is empty')
  };

  const errorConfig = [
    {
      enabled: !!listDirectoryError,
      message: t('An error occurred while fetching the data'),
      action: t('Retry'),
      onClick: reloadData
    }
  ];

  return (
    <>
      <div className="hue-storage-browser__actions-bar">
        <Input
          className="hue-storage-browser__search"
          placeholder={t('Search')}
          allowClear={true}
          onChange={event => {
            handleSearch(event.target.value);
          }}
        />
        <div className="hue-storage-browser__actions-bar-right">
          <StorageBrowserActions
            currentPath={fileStats.path}
            isTrashEnabled={filesData?.is_trash_enabled}
            selectedFiles={selectedFiles}
            setLoadingFiles={setLoadingFiles}
            onSuccessfulAction={reloadData}
          />
          <CreateAndUploadAction
            currentPath={fileStats.path}
            setLoadingFiles={setLoadingFiles}
            onSuccessfulAction={reloadData}
            onFilesUpload={onFilesDrop}
          />
        </div>
      </div>

      <DragAndDrop onDrop={onFilesDrop}>
        <LoadingErrorWrapper loading={loadingFiles || listDirectoryLoading} errors={errorConfig}>
          <Table
            className={className}
            columns={getColumns(tableData[0] ?? {})}
            dataSource={tableData}
            onRow={onRowClicked}
            pagination={false}
            rowClassName={rowClassName}
            rowKey={r => `${r.path}_${r.type}_${r.mtime}`}
            rowSelection={{
              type: 'checkbox',
              ...rowSelection
            }}
            scroll={{ y: tableHeight }}
            data-testid={`${testId}`}
            locale={locale}
            {...restProps}
          />

          {filesData?.page && filesData?.page?.total_count > 0 && (
            <Pagination
              onNextPageButtonClicked={onNextPageButtonClicked}
              onPageNumberChange={setPageNumber}
              onPageSizeChange={setPageSize}
              onPreviousPageButtonClicked={onPreviousPageButtonClicked}
              pageSize={pageSize}
              pageStats={filesData?.page}
            />
          )}
        </LoadingErrorWrapper>
      </DragAndDrop>
      {filesToUpload.length > 0 && (
        <FileUploadQueue
          filesQueue={filesToUpload}
          onClose={() => setFilesToUpload([])}
          onComplete={reloadData}
        />
      )}
    </>
  );
};

StorageDirectoryPage.defaultProps = defaultProps;
export default StorageDirectoryPage;
