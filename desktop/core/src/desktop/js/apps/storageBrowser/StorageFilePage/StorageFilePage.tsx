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

import React, { useMemo } from 'react';
import { PathAndFileData } from '../../../reactComponents/FileChooser/types';
import './StorageFilePage.scss';
import { i18nReact } from '../../../utils/i18nReact';
import Button, { PrimaryButton } from 'cuix/dist/components/Button';
import { getFileMetaData } from './StorageFilePage.util';
import { DOWNLOAD_API_URL, SAVE_FILE_API_URL } from '../../../reactComponents/FileChooser/api';
import huePubSub from '../../../utils/huePubSub';
import useSaveData from '../../../utils/hooks/useSaveData';
import {
  EDITABLE_FILE_FORMATS,
  SUPPORTED_FILE_EXTENSIONS,
  SupportedFileTypes
} from '../../../utils/constants/storageBrowser';
import { Spin } from 'antd';

const StorageFilePage = ({ fileData }: { fileData: PathAndFileData }): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [isEditing, setIsEditing] = React.useState(false);
  const [fileContent, setFileContent] = React.useState(fileData.view?.contents);
  const fileMetaData = useMemo(() => getFileMetaData(t, fileData), [t, fileData]);

  const { loading: isSaving, save } = useSaveData(SAVE_FILE_API_URL);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFileContent(fileData.view?.contents);
  };

  const handleSave = () => {
    setIsEditing(false);
    save(
      {
        path: fileData.path,
        encoding: 'utf-8',
        contents: fileContent
      },
      {
        onError: () => {
          setIsEditing(true);
        },
        onSuccess: () => {
          huePubSub.publish('hue.global.info', { message: t('Changes saved!') });
        }
      }
    );
  };

  const handleDownload = () => {
    huePubSub.publish('hue.global.info', { message: t('Downloading your file, Please wait...') });
  };

  const filePreviewUrl = `${DOWNLOAD_API_URL}${fileData.path}?disposition=inline`;

  const fileName = fileData?.path?.split('/')?.pop();
  const fileType = useMemo(() => {
    const fileExtension = fileName?.split('.')?.pop()?.toLocaleLowerCase();
    if (!fileExtension) {
      return SupportedFileTypes.OTHER;
    }
    return SUPPORTED_FILE_EXTENSIONS[fileExtension] ?? SupportedFileTypes.OTHER;
  }, [fileName]);

  const isEditingEnabled =
    !isEditing &&
    fileData.editable &&
    EDITABLE_FILE_FORMATS[fileType] &&
    fileData?.view?.compression?.toLocaleLowerCase() === 'none';

  return (
    <Spin spinning={isSaving}>
      <div className="hue-storage-file-page">
        <div className="meta-data">
          {fileMetaData.map((row, index) => (
            <div key={'meta-data-group' + index} className="meta-data__group">
              {row.map(item => (
                <div key={item.name} className="meta-data__column">
                  <div className="meta-data__column-label">{item.label}</div>
                  <div className="meta-data__column-value">{item.value}</div>
                </div>
              ))}
            </div>
          ))}
        </div>

        <div className="preview">
          <div className="preview__title-bar">
            {t('Content')}
            <div className="preview__action-group">
              {isEditingEnabled && (
                <PrimaryButton
                  data-testid="preview--edit--button"
                  data-event=""
                  onClick={handleEdit}
                >
                  {t('Edit')}
                </PrimaryButton>
              )}
              {isEditing && (
                <>
                  <PrimaryButton
                    data-testid="preview--save--button"
                    data-event=""
                    onClick={handleSave}
                    disabled={fileContent === fileData.view?.contents}
                  >
                    {t('Save')}
                  </PrimaryButton>
                  <Button
                    role="button"
                    data-testid="preview--cancel--button"
                    data-event=""
                    onClick={handleCancel}
                  >
                    {t('Cancel')}
                  </Button>
                </>
              )}
              {fileData.show_download_button && (
                <a href={`${DOWNLOAD_API_URL}${fileData.path}`}>
                  <PrimaryButton
                    data-testid="preview--download--button"
                    data-event=""
                    onClick={handleDownload}
                  >
                    {t('Download')}
                  </PrimaryButton>
                </a>
              )}
            </div>
          </div>

          <div className="preview__content">
            {fileType === SupportedFileTypes.TEXT && (
              <textarea
                value={fileContent}
                onChange={e => setFileContent(e.target.value)}
                readOnly={!isEditing}
                className="preview__textarea"
              />
            )}

            {fileType === SupportedFileTypes.IMAGE && <img src={filePreviewUrl} alt={fileName} />}

            {fileType === SupportedFileTypes.DOCUMENT && (
              <div className="preview__document">
                <div>
                  <PrimaryButton
                    data-testid=""
                    data-event=""
                    onClick={() => window.open(filePreviewUrl)}
                  >
                    {t('Preview document')}
                  </PrimaryButton>
                </div>
                <div>{t('The Document will open in a new tab.')}</div>
              </div>
            )}

            {fileType === SupportedFileTypes.AUDIO && (
              <audio controls preload="auto" data-testid="preview__content__audio">
                <source src={filePreviewUrl} />
                {t('Your browser does not support the audio element.')}
              </audio>
            )}

            {fileType === SupportedFileTypes.VIDEO && (
              <video controls preload="auto" data-testid="preview__content__video">
                <source src={filePreviewUrl} />
                {t('Your browser does not support the video element.')}
              </video>
            )}

            {fileType === SupportedFileTypes.OTHER && (
              <div className="preview__unsupported">
                {t('Preview not available for this file. Please download the file to view.')}
                <br />
                {t(`Supported file extensions: 
                ${Object.keys(SUPPORTED_FILE_EXTENSIONS).join(', ')}`)}
              </div>
            )}
          </div>
        </div>
      </div>
    </Spin>
  );
};

export default StorageFilePage;
