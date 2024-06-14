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

import React, { useState, useEffect } from 'react';
import { Spin } from 'antd';

import { i18nReact } from '../../../../utils/i18nReact';
import BucketIcon from '@cloudera/cuix-core/icons/react/BucketIcon';

import PathBrowser from '../../../../reactComponents/FileChooser/PathBrowser/PathBrowser';
import StorageBrowserTable from '../StorageBrowserTable/StorageBrowserTable';
import { fetchFiles } from '../../../../reactComponents/FileChooser/api';
import {
  PathAndFileData,
  StorageBrowserTableData,
  PageStats,
  SortOrder
} from '../../../../reactComponents/FileChooser/types';

import './StorageBrowserTabContent.scss';

interface StorageBrowserTabContentProps {
  user_home_dir: string;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-storage-browser-tabContent'
};

const StorageBrowserTabContent = ({
  user_home_dir,
  testId
}: StorageBrowserTabContentProps): JSX.Element => {
  const [filePath, setFilePath] = useState<string>(user_home_dir);
  const [filesData, setFilesData] = useState<PathAndFileData>();
  const [files, setFiles] = useState<StorageBrowserTableData[]>();
  const [loadingFiles, setLoadingFiles] = useState(true);
  const [pageStats, setPageStats] = useState<PageStats>();
  const [pageSize, setPageSize] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [sortByColumn, setSortByColumn] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<SortOrder>(SortOrder.NONE);
  //TODO: Add filter functionality
  const [filterData] = useState<string>('');

  const [refreshKey, setRefreshKey] = useState<number>(0);

  const { t } = i18nReact.useTranslation();

  useEffect(() => {
    setLoadingFiles(true);
    fetchFiles(filePath, pageSize, pageNumber, filterData, sortByColumn, sortOrder)
      .then(responseFilesData => {
        setFilesData(responseFilesData);
        const tableData: StorageBrowserTableData[] = responseFilesData.files.map(file => ({
          name: file.name,
          size: file.humansize,
          user: file.stats.user,
          group: file.stats.group,
          permission: file.rwx,
          mtime: file.mtime,
          type: file.type,
          path: file.path
        }));
        setFiles(tableData);
        setPageStats(responseFilesData.page);
        setPageSize(responseFilesData.pagesize);
      })
      .catch(error => {
        //TODO: handle errors
        console.error(error);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  }, [filePath, pageSize, pageNumber, sortByColumn, sortOrder, refreshKey]);

  return (
    <Spin spinning={loadingFiles}>
      <div className="hue-storage-browser-tabContent" data-testid={testId}>
        <div className="hue-storage-browser__title-bar" data-testid={`${testId}-title-bar`}>
          <BucketIcon className="hue-storage-browser__icon" data-testid={`${testId}-icon`} />
          <h3 className="hue-storage-browser__folder-name" data-testid={`${testId}-folder-namer`}>
            {filesData?.breadcrumbs[filesData?.breadcrumbs?.length - 1].label}
          </h3>
        </div>
        <div
          className="hue-storage-browser__path-browser-panel"
          data-testid={`${testId}-path-browser-panel`}
        >
          <span className="hue-storage-browser__filePath">{t('File Path:')}</span>
          <PathBrowser
            breadcrumbs={filesData?.breadcrumbs}
            onFilepathChange={setFilePath}
            seperator={'/'}
            showIcon={false}
          />
        </div>
        <StorageBrowserTable
          dataSource={files}
          pageStats={pageStats}
          pageSize={pageSize}
          onFilepathChange={setFilePath}
          onPageSizeChange={setPageSize}
          onPageNumberChange={setPageNumber}
          onSortByColumnChange={setSortByColumn}
          onSortOrderChange={setSortOrder}
          sortByColumn={sortByColumn}
          sortOrder={sortOrder}
          setRefreshKey={setRefreshKey}
          setLoadingFiles={setLoadingFiles}
          filePath={filePath}
        />
      </div>
    </Spin>
  );
};

StorageBrowserTabContent.defaultProps = defaultProps;

export default StorageBrowserTabContent;
