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

import React, { useState, useEffect, useMemo } from 'react';
import Modal from 'antd/lib/modal/Modal';
import { Col, Menu, Row, Spin, Button } from 'antd';

import HdfsIcon from '../../../components/icons/HdfsIcon';
import S3Icon from '../../../components/icons/S3Icon';
import AdlsIcon from '../../../components/icons/AdlsIcon';

import { ApiFileSystem, FILESYSTEMS_API_URL, VIEWFILES_API_URl } from '../api';
import { FileSystem, PathAndFileData } from '../types';
import './FileChooserModal.scss';
import PathBrowser from '../PathBrowser/PathBrowser';
import useLoadData from '../../../utils/hooks/useLoadData';

interface FileProps {
  show: boolean;
  onCancel: () => void;
  title?: string;
  okText?: string;
}

const defaultProps = { title: 'Choose a file', okText: 'Select' };

const FileChooserModal: React.FC<FileProps> = ({ show, onCancel, title, okText }) => {
  const [filePath, setFilePath] = useState<string | undefined>();

  const icons = {
    hdfs: <HdfsIcon />,
    abfs: <AdlsIcon />,
    s3: <S3Icon />
  };

  //temporary until the file is selected through the file chooser component
  const handleOk = onCancel;
  const handleCancel = onCancel;

  const { data: fileSystemsData, loading: loadingFilesSystem } =
    useLoadData<ApiFileSystem[]>(FILESYSTEMS_API_URL);

  const fileSystemList: FileSystem[] | undefined = useMemo(
    () =>
      fileSystemsData?.map((system, index) => {
        return {
          label: system.file_system,
          key: index,
          icon: icons[system.file_system],
          user_home_dir: system.user_home_directory
        };
      }),
    [fileSystemsData]
  );

  useEffect(() => {
    if (fileSystemsData && fileSystemsData?.length !== 0) {
      setFilePath(fileSystemsData[0].user_home_directory);
    }
  }, [fileSystemsData]);

  const { data: filesData, loading: loadingFiles } = useLoadData<PathAndFileData>(filePath, {
    urlPrefix: VIEWFILES_API_URl,
    skip: !!filePath
  });

  return (
    <Modal
      title={title}
      open={show}
      onOk={handleOk}
      onCancel={handleCancel}
      okText={okText}
      width={930}
      className="hue-file-chooser__modal"
    >
      <Spin spinning={loadingFilesSystem || loadingFiles}>
        <Row>
          <Col span={5}>
            <Menu
              items={fileSystemList}
              onSelect={selectedMenuItem => {
                setFilePath(fileSystemList?.[selectedMenuItem.key].user_home_dir);
              }}
              className="hue-file-system__panel"
            ></Menu>
          </Col>
          <Col span={19}>
            <Spin spinning={loadingFiles}>
              <Row className="hue-path-browser-panel" onClick={e => e.stopPropagation()}>
                <Col span={18}>
                  <PathBrowser
                    breadcrumbs={filesData?.breadcrumbs}
                    onFilepathChange={setFilePath}
                    seperator={'>'}
                    showIcon={true}
                  ></PathBrowser>
                </Col>
                <Col span={3}>
                  <Button className="hue-path-browser-panel__button">New Folder</Button>
                </Col>
                <Col span={3}>
                  <Button className="hue-path-browser-panel__button">Upload</Button>
                </Col>
              </Row>
            </Spin>
          </Col>
        </Row>
      </Spin>
    </Modal>
  );
};

FileChooserModal.defaultProps = defaultProps;

export default FileChooserModal;
