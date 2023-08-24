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

import BucketIcon from '@cloudera/cuix-core/icons/react/BucketIcon';
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
          className="hue-storage-browser-pathBrowserPanel"
          data-testid={`${testId}-pathBrowserPanel`}
        >
          <div className="hue-storage-browser-filePath">File Path:</div>
          <PathBrowser
            breadcrumbs={filesData?.breadcrumbs}
            handleFilePathChange={setFilePath}
            seperator={'/'}
            showIcon={false}
          />
        </div>
      </div>
    </Spin>
  );
};

StorageBrowserTabContent.defaultProps = defaultProps;

export default StorageBrowserTabContent;
