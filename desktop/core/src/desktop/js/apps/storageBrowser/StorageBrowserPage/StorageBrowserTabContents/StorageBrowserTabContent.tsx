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
import { Spin, Input, Dropdown, Button } from 'antd';
import type { MenuProps } from 'antd';

import { i18nReact } from '../../../../utils/i18nReact';
import BucketIcon from '@cloudera/cuix-core/icons/react/BucketIcon';
import CopyClipboardIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';
import DataMovementIcon from '@cloudera/cuix-core/icons/react/DataMovementIcon';
import DeleteIcon from '@cloudera/cuix-core/icons/react/DeleteIcon';
import DownloadIcon from '@cloudera/cuix-core/icons/react/DownloadIcon';
import DropDownIcon from '@cloudera/cuix-core/icons/react/DropdownIcon';
import FolderIcon from '@cloudera/cuix-core/icons/react/ProjectIcon';
import ImportIcon from '@cloudera/cuix-core/icons/react/ImportIcon';
import PlusCircleIcon from '@cloudera/cuix-core/icons/react/PlusCircleIcon';
//TODO: Use cuix icon (Currently fileIcon does not exist in cuix)
import { FileOutlined } from '@ant-design/icons';

import PathBrowser from '../../../../reactComponents/FileChooser/PathBrowser/PathBrowser';
import InputModal from '../../InputModal/InputModal';
import StorageBrowserTable from '../StorageBrowserTable/StorageBrowserTable';
import { fetchFiles, mkdir, touch } from '../../../../reactComponents/FileChooser/api';
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

const StorageBrowserTabContent: React.FC<StorageBrowserTabContentProps> = ({
  user_home_dir,
  testId
}): JSX.Element => {
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
  const [showNewFolderModal, setShowNewFolderModal] = useState<boolean>(false);
  const [showNewFileModal, setShowNewFileModal] = useState<boolean>(false);
  const [refreshKey, setRefreshKey] = useState<number>(0);

  const { t } = i18nReact.useTranslation();

  const newActionsMenuItems: MenuProps['items'] = [
    {
      key: 'create',
      type: 'group',
      label: t('CREATE'),
      children: [
        {
          icon: <FileOutlined />,
          key: 'new_file',
          label: t('New File'),
          onClick: () => {
            setShowNewFileModal(true);
          }
        },
        {
          icon: <FolderIcon />,
          key: 'new_folder',
          label: t('New Folder'),
          onClick: () => {
            setShowNewFolderModal(true);
          }
        }
      ]
    },
    {
      key: 'upload',
      type: 'group',
      label: t('UPLOAD'),
      children: [
        {
          icon: <ImportIcon />,
          key: 'upload',
          label: t('New Upload')
        }
      ]
    }
  ];

  const bulkActionsMenuItems: MenuProps['items'] = [
    {
      icon: <CopyClipboardIcon />,
      key: 'copy',
      label: t('Copy')
    },
    {
      icon: <DataMovementIcon />,
      key: 'move',
      label: t('Move')
    },
    {
      icon: <DownloadIcon />,
      key: 'download',
      label: t('Download')
    },
    {
      icon: <DeleteIcon />,
      key: 'delete',
      label: t('Delete')
    }
  ];

  const handleCreateNewFolder = (folderName: string) => {
    setLoadingFiles(true);
    mkdir(folderName, filePath)
      .then(() => {
        setRefreshKey(oldKey => oldKey + 1);
      })
      .catch(error => {
        // eslint-disable-next-line no-restricted-syntax
        console.log(error);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  };

  const handleCreateNewFile = (fileName: string) => {
    setLoadingFiles(true);
    touch(fileName, filePath)
      .then(() => {
        setRefreshKey(oldKey => oldKey + 1);
      })
      .catch(error => {
        // eslint-disable-next-line no-restricted-syntax
        console.log(error);
      })
      .finally(() => {
        setLoadingFiles(false);
      });
  };

  useEffect(() => {
    setLoadingFiles(true);
    fetchFiles(filePath, pageSize, pageNumber, filterData, sortByColumn, sortOrder)
      .then(responseFilesData => {
        setFilesData(responseFilesData);
        const tableData: StorageBrowserTableData[] = responseFilesData.files.map(file => ({
          name: file.name,
          size: file.humansize,
          user: file.stats.user,
          groups: file.stats.group,
          permission: file.rwx,
          lastUpdated: file.mtime,
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
          <div className="hue-storage-browser__folder-name" data-testid={`${testId}-folder-namer`}>
            {filesData?.breadcrumbs[filesData?.breadcrumbs?.length - 1].label}
          </div>
        </div>
        <div
          className="hue-storage-browser__path-browser-panel"
          data-testid={`${testId}-path-browser-panel`}
        >
          <div className="hue-storage-browser__filePath">{t('File Path:')}</div>
          <PathBrowser
            breadcrumbs={filesData?.breadcrumbs}
            onFilepathChange={setFilePath}
            seperator={'/'}
            showIcon={false}
          />
        </div>
        <div className="hue-storage-browser__actions-bar">
          <Input className="hue-storage-browser__search" placeholder={t('Search')} />
          <div className="hue-storage-browser__actions-bar-right">
            <Dropdown
              overlayClassName="hue-storage-browser__actions-dropdown"
              menu={{
                items: bulkActionsMenuItems,
                className: 'hue-storage-browser__action-menu'
              }}
              trigger={['hover', 'click']}
            >
              <Button className="hue-storage-browser__bulk-action-btn">
                {t('Bulk Actions')}
                <DropDownIcon />
              </Button>
            </Dropdown>
            <Dropdown
              overlayClassName="hue-storage-browser__actions-dropdown"
              menu={{
                items: newActionsMenuItems,
                className: 'hue-storage-browser__action-menu'
              }}
              trigger={['hover', 'click']}
            >
              <Button className="hue-storage-browser__new-btn" icon={<PlusCircleIcon />}>
                {t('New')}
                <DropDownIcon />
              </Button>
            </Dropdown>
          </div>
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
        />
        <InputModal
          title={t('Create New Folder')}
          inputLabel={t('Enter Folder name here')}
          submitText={t('Create')}
          showModal={showNewFolderModal}
          onSubmit={handleCreateNewFolder}
          onClose={() => setShowNewFolderModal(false)}
        />
        <InputModal
          title={t('Create New File')}
          inputLabel={t('Enter File name here')}
          submitText={t('Create')}
          showModal={showNewFileModal}
          onSubmit={handleCreateNewFile}
          onClose={() => setShowNewFileModal(false)}
        />
      </div>
    </Spin>
  );
};

StorageBrowserTabContent.defaultProps = defaultProps;

export default StorageBrowserTabContent;
