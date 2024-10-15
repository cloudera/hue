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
import { Spin } from 'antd';

import { i18nReact } from '../../../../utils/i18nReact';
import BucketIcon from '@cloudera/cuix-core/icons/react/BucketIcon';

import PathBrowser from '../../../../reactComponents/FileChooser/PathBrowser/PathBrowser';
import StorageBrowserTable from '../StorageBrowserTable/StorageBrowserTable';
import { VIEWFILES_API_URl, trashPath } from '../../../../reactComponents/FileChooser/api';
import {
  BrowserViewType,
  PathAndFileData,
  SortOrder
} from '../../../../reactComponents/FileChooser/types';
import { DEFAULT_PAGE_SIZE } from '../../../../utils/constants/storageBrowser';
import useLoadData from '../../../../utils/hooks/useLoadData';

import './StorageBrowserTabContent.scss';
import StorageFilePage from '../../StorageFilePage/StorageFilePage';
import { BorderlessButton } from 'cuix/dist/components/Button';
import { inTrash, isHDFS } from '../../../../utils/storageBrowserUtils';
import huePubSub from '../../../../utils/huePubSub';

interface StorageBrowserTabContentProps {
  user_home_dir: string;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-storage-browser-tab-content'
};

const StorageBrowserTabContent = ({
  user_home_dir,
  testId
}: StorageBrowserTabContentProps): JSX.Element => {
  const [filePath, setFilePath] = useState<string>(user_home_dir);
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [sortByColumn, setSortByColumn] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<SortOrder>(SortOrder.NONE);
  const [searchTerm, setSearchTerm] = useState<string>('');

  const { t } = i18nReact.useTranslation();

  const {
    data: filesData,
    loading,
    reloadData
  } = useLoadData<PathAndFileData>(filePath, {
    urlPrefix: VIEWFILES_API_URl,
    params: {
      pagesize: pageSize.toString(),
      pagenum: pageNumber.toString(),
      filter: searchTerm,
      sortby: sortByColumn,
      descending: sortOrder === SortOrder.DSC ? 'true' : 'false'
    },
    skip: filePath === '' || filePath === undefined
  });

  const getTrashPath = () => {
    // trashPath(filePath)
    //   .then(response => {
    //     // eslint-disable-next-line no-restricted-syntax
    //     console.log(response);
    //   })
    //   .catch(error => {
    //     huePubSub.publish('hue.error', error);
    //   })
    //   .finally(() => {});
    setFilePath('/user/demo/.Trash/241008080000/user/demo');
  };

  return (
    <Spin spinning={loading}>
      <div className="hue-storage-browser-tab-content" data-testid={testId}>
        <div className="hue-storage-browser__title-bar" data-testid={`${testId}-title-bar`}>
          <BucketIcon className="hue-storage-browser__icon" data-testid={`${testId}-icon`} />
          <h3 className="hue-storage-browser__folder-name" data-testid={`${testId}-folder-namer`}>
            {filesData?.path?.split('/').pop()}
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
          {isHDFS(filePath) && !inTrash(filePath) ? (
            <BorderlessButton data-event={''} onClick={() => {
              getTrashPath();
            }}>VIEW TRASH FOLDER</BorderlessButton>
          ) : (
            <div></div>
          )}
        </div>
        {filesData?.type === BrowserViewType.file ? (
          <StorageFilePage fileData={filesData} />
        ) : (
          <StorageBrowserTable
            filesData={filesData}
            pageSize={pageSize}
            onFilepathChange={setFilePath}
            onPageSizeChange={setPageSize}
            onPageNumberChange={setPageNumber}
            onSortByColumnChange={setSortByColumn}
            onSortOrderChange={setSortOrder}
            onSearch={setSearchTerm}
            sortByColumn={sortByColumn}
            sortOrder={sortOrder}
            refetchData={reloadData}
            filePath={filePath}
          />
        )}
      </div>
    </Spin>
  );
};

StorageBrowserTabContent.defaultProps = defaultProps;

export default StorageBrowserTabContent;
