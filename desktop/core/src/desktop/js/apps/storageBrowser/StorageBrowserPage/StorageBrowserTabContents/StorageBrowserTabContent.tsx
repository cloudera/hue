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
import {
  FileOutlined,
  CaretDownOutlined,
  PlusCircleOutlined,
  CopyOutlined,
  DownloadOutlined,
  DeleteOutlined,
  SwapOutlined,
  FolderOutlined,
  UploadOutlined
} from '@ant-design/icons';

import PathBrowser from '../../../../reactComponents/FileChooser/PathBrowser/PathBrowser';
import { fetchFiles } from '../../../../reactComponents/FileChooser/api';
import { PathAndFileData } from '../../../../reactComponents/FileChooser/types';

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
  const [filesData, setFilesData] = useState<PathAndFileData | undefined>();
  const [loadingFiles, setloadingFiles] = useState(true);

  const { t } = i18nReact.useTranslation();

  const newActionsMenuItems: MenuProps['items'] = [
    {
      key: 'create',
      type: 'group',
      label: 'CREATE',
      children: [
        {
          icon: <FileOutlined />,
          key: 'new_file',
          label: 'New File'
        },
        {
          icon: <FolderOutlined />,
          key: 'new_folder',
          label: 'New Folder'
        }
      ]
    },
    {
      key: 'upload',
      type: 'group',
      label: 'UPLOAD',
      children: [
        {
          icon: <UploadOutlined />,
          key: 'upload_file',
          label: 'File'
        },
        {
          icon: <UploadOutlined />,
          key: 'upload_folder',
          label: 'Folder'
        },
        {
          icon: <UploadOutlined />,
          key: 'upload_zip',
          label: 'Zip Folder'
        }
      ]
    }
  ];

  const bulkActionsMenuItems: MenuProps['items'] = [
    {
      icon: <CopyOutlined />,
      key: 'copy',
      label: 'Copy'
    },
    {
      icon: <SwapOutlined />,
      key: 'move',
      label: 'Move'
    },
    {
      icon: <DownloadOutlined />,
      key: 'download',
      label: 'Download'
    },
    {
      icon: <DeleteOutlined />,
      key: 'delete',
      label: 'Delete'
    }
  ];

  useEffect(() => {
    setloadingFiles(true);
    fetchFiles(filePath)
      .then(responseFilesData => {
        setFilesData(responseFilesData);
      })
      .catch(error => {
        //TODO: handle errors
      })
      .finally(() => {
        setloadingFiles(false);
      });
  }, [filePath]);

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
          <Input className="hue-storage-browser__search" placeholder={'Search'} />
          <div className="hue-storage-browser__actions-bar-right">
            <Dropdown
              overlayClassName="hue-storage-browser__bulk-action"
              menu={{
                items: bulkActionsMenuItems,
                className: 'hue-storage-browser__action-menu'
              }}
              trigger={['hover', 'click']}
            >
              <Button className="hue-storage-browser__bulk-action-btn">
                Bulk Actions
                <CaretDownOutlined />
              </Button>
            </Dropdown>
            <Dropdown
              overlayClassName="hue-storage-browser__new-action"
              menu={{
                items: newActionsMenuItems,
                className: 'hue-storage-browser__action-menu'
              }}
              trigger={['hover', 'click']}
            >
              <Button className="hue-storage-browser__new-btn" icon={<PlusCircleOutlined />}>
                New
                <CaretDownOutlined />
              </Button>
            </Dropdown>
          </div>
        </div>
      </div>
    </Spin>
  );
};

StorageBrowserTabContent.defaultProps = defaultProps;

export default StorageBrowserTabContent;
