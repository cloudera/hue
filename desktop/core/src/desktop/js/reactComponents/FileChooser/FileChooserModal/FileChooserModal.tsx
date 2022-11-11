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
import Modal from 'antd/lib/modal/Modal';

import HdfsIcon from '../../../components/icons/HdfsIcon';
import S3Icon from '../../../components/icons/S3Icon';
import AdlsIcon from '../../../components/icons/AdlsIcon';

import { fetchFileSystems } from '../api';
import { FileSystem } from '../types';
import FileSystemList from '../FileSystemList/FileSystemList';
interface FileProps {
  show: boolean;
  onCancel: () => void;
  title: string;
  okText: string;
}

const defaultProps = { title: 'Choose a file', okText: 'Select' };

const FileChooserModal: React.FC<FileProps> = ({ show, onCancel, title, okText }) => {
  const [fileSystemList, setFileSystemList] = useState<Array<FileSystem>>([]);

  const icons = {
    hdfs: <HdfsIcon />,
    abfs: <AdlsIcon />,
    s3: <S3Icon />
  };

  const handleOk = () => {
    //temporary until the file is selected through the file chooser component
    onCancel();
  };

  const handleCancel = () => {
    onCancel();
  };

  useEffect(() => {
    if (show) {
      fetchFileSystems().then(fileSystemResponse => {
        const fileSystems = Object.keys(fileSystemResponse.filesystems);
        if (fileSystems !== undefined || fileSystems.length !== 0) {
          const fileSystemsObj = fileSystems.map(system => {
            return {
              label: system,
              key: system,
              icon: icons[system]
            };
          });
          setFileSystemList(fileSystemsObj);
        }
      });
    }
  }, [show]);

  return (
    <Modal
      title={title}
      open={show}
      onOk={handleOk}
      onCancel={handleCancel}
      okText={okText}
      width={930}
      bodyStyle={{ height: '554px', padding: '0px' }}
    >
      <FileSystemList fileSystems={fileSystemList}></FileSystemList>
    </Modal>
  );
};

FileChooserModal.defaultProps = defaultProps;

export default FileChooserModal;
