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
import Button from 'cuix/dist/components/Button';
import S3Icon from '@cloudera/cuix-core/icons/react/S3Icon';
import HDFSIcon from '@cloudera/cuix-core/icons/react/HdfsIcon';
import OzoneIcon from '@cloudera/cuix-core/icons/react/OzoneIcon';
import GoogleCloudIcon from '@cloudera/cuix-core/icons/react/GoogleCloudIcon';
import AdlsIcon from '../../../components/icons/AdlsIcon';

import { hueWindow } from 'types/types';

import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import FileChooserModal from '../../storageBrowser/FileChooserModal/FileChooserModal';
import LocalFileUploadOption from './LocalFileUploadOption';
import { FILESYSTEMS_API_URL } from '../../storageBrowser/api';
import { FileMetaData, ImporterFileSource } from '../types';
import { FileSystem } from '../../storageBrowser/types';
import { i18nReact } from '../../../utils/i18nReact';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';

import './ImporterSourceSelector.scss';

const fileSystems = {
  s3a: {
    icon: <S3Icon />,
    title: 'Amazon S3'
  },
  hdfs: {
    icon: <HDFSIcon />,
    title: 'HDFS'
  },
  abfs: {
    icon: <AdlsIcon />,
    title: 'Azure Storage'
  },
  ofs: {
    icon: <OzoneIcon />,
    title: 'Ozone'
  },
  adls: {
    icon: <AdlsIcon />,
    title: 'Azure Storage'
  },
  gs: {
    icon: <GoogleCloudIcon />,
    title: 'Google Storage'
  }
};

interface ImporterSourceSelectorProps {
  setFileMetaData: (fileMetaData: FileMetaData) => void;
}

const ImporterSourceSelector = ({ setFileMetaData }: ImporterSourceSelectorProps): JSX.Element => {
  const [selectedUserHomeDirectory, setSelectedUserHomeDirectory] = useState<string | undefined>(
    undefined
  );
  const [uploadError, setUploadError] = useState<string | undefined>(undefined);
  const { t } = i18nReact.useTranslation();

  const {
    data: fileSystemsData,
    loading,
    error,
    reloadData
  } = useLoadData<FileSystem[]>(FILESYSTEMS_API_URL);

  const errorConfig = [
    {
      enabled: !!error,
      message: t('An error occurred while fetching the filesystem'),
      action: t('Retry'),
      onClick: reloadData
    },
    {
      enabled: !!uploadError,
      message: uploadError
    }
  ];

  const fileSystems = {
    s3a: {
      icon: <S3Icon />,
      title: 'Amazon S3'
    },
    hdfs: {
      icon: <HDFSIcon />,
      title: 'Hadoop Distributed File System'
    },
    abfs: {
      icon: <AdlsIcon />,
      title: 'Azure Blob File System'
    },
    ofs: {
      icon: <OzoneIcon />,
      title: 'Ozone File System'
    }
  };

  const handleUploadClick = () => {
    if (!uploadRef || !uploadRef.current) {
      return;
    }
    uploadRef.current.click();
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) {
      return;
    }

    const file = files[0];

    const payload = new FormData();
    payload.append('file', file);

    const file_size = file.size;
    if (file_size === 0) {
      huePubSub.publish('hue.global.warning', {
        message: t('This file is empty, please select another file.')
      });
    } else if (file_size > 200 * 1000) {
      huePubSub.publish('hue.global.warning', {
        message: t(
          'File size exceeds the supported size (200 KB). Please use the S3, ABFS or HDFS browser to upload files.'
        )
      });
    } else {
      upload(payload, {
        onSuccess: data => {
          setFileMetaData({
            path: data.file_path,
            fileName: file.name,
            source: ImporterFileSource.LOCAL
          });
        },
        onError: error => {
          huePubSub.publish('hue.error', error);
        }
      });
    }
  };

  const handleFileSelection = async (destination_path: string) => {
  const handleFileSelection = async (destinationPath: string) => {
    setFileMetaData({
      path: destinationPath,
      source: ImporterFileSource.REMOTE
    });
  };

  return (
    <LoadingErrorWrapper loading={loading} errors={errorConfig}>
      <div className="hue-importer__source-selector cuix antd">
        <div className="hue-importer__source-selector-title">
          {t('Select a source to import from')}
        </div>
        <div className="hue-importer__source-selector-options">
          {(window as hueWindow).ENABLE_DIRECT_UPLOAD && (
            <LocalFileUploadOption
              setFileMetaData={setFileMetaData}
              setUploadError={setUploadError}
            />
          )}
          {fileSystemsData?.map(filesystem => (
            <div className="hue-importer__source-selector-option" key={filesystem.name}>
              <Button
                className="hue-importer__source-selector-option-button"
                size="large"
                icon={fileSystems[filesystem.name].icon}
                onClick={() => {
                  setSelectedUserHomeDirectory(filesystem.userHomeDirectory);
                }}
              ></Button>
              <span className="hue-importer__source-selector-option-btn-title">
                {t(fileSystems[filesystem.name].title)}
              </span>
            </div>
          ))}
        </div>
      </div>
      {selectedUserHomeDirectory && (
        <FileChooserModal
          onClose={() => {
            setSelectedUserHomeDirectory(undefined);
          }}
          onSubmit={handleFileSelection}
          showModal={true}
          title={t('Import file')}
          sourcePath={selectedUserHomeDirectory}
          isFileSelectionAllowed={true}
          isUploadEnabled={true}
        />
      )}
    </LoadingErrorWrapper>
  );
};

export default ImporterSourceSelector;
