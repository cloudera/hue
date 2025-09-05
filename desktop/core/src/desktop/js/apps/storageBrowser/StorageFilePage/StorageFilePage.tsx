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

import React, { useMemo, useState } from 'react';
import { BrowserViewType, FilePreview, FileStats } from '../types';
import './StorageFilePage.scss';
import { i18nReact } from '../../../utils/i18nReact';
import Button, { PrimaryButton } from 'cuix/dist/components/Button';
import { getFileMetaData, getFileType } from './StorageFilePage.util';
import { DOWNLOAD_API_URL, FILE_PREVIEW_API_URL, SAVE_FILE_API_URL } from '../api';
import huePubSub from '../../../utils/huePubSub';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import Pagination from '../../../reactComponents/Pagination/Pagination';
import {
  DEFAULT_PREVIEW_PAGE_SIZE,
  EDITABLE_FILE_FORMATS,
  SupportedFileTypes
} from '../../../utils/constants/storageBrowser';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { getLastKnownConfig } from '../../../config/hueConfig';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import { inTrash } from '../utils/utils';
import { getLastDirOrFileNameFromPath } from '../../../reactComponents/PathBrowser/PathBrowser.util';

interface StorageFilePageProps {
  onReload: () => void;
  fileStats: FileStats;
}

const StorageFilePage = ({ fileStats, onReload }: StorageFilePageProps): JSX.Element => {
  const config = getLastKnownConfig();
  const fileName = getLastDirOrFileNameFromPath(fileStats.path);
  const fileType = getFileType(fileName);

  const { t } = i18nReact.useTranslation();

  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [fileContent, setFileContent] = useState<FilePreview['contents']>();
  const [pageNumber, setPageNumber] = useState<number>(1);
  const pageSize = DEFAULT_PREVIEW_PAGE_SIZE;
  const pageOffset = (pageNumber - 1) * pageSize;

  const { loading: isSaving, save } = useSaveData(SAVE_FILE_API_URL, {
    options: { qsEncodeData: true } // TODO: Remove once API supports RAW JSON payload
  });

  const { data, loading, error } = useLoadData<FilePreview>(FILE_PREVIEW_API_URL, {
    params: {
      path: fileStats.path,
      offset: pageOffset,
      length: pageSize
    },
    onSuccess: d => setFileContent(d.contents),
    skip:
      fileStats.path === '' ||
      fileStats.path === undefined ||
      fileStats?.type !== BrowserViewType.file ||
      !EDITABLE_FILE_FORMATS.has(fileType)
  });

  const fileMetaData = useMemo(() => getFileMetaData(t, fileStats), [t, fileStats]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFileContent(data?.contents);
  };

  const handleSave = () => {
    setIsEditing(false);
    save(
      {
        path: fileStats.path,
        encoding: 'utf-8',
        contents: fileContent
      },
      {
        onError: () => {
          setIsEditing(true);
        },
        onSuccess: () => {
          onReload();
          huePubSub.publish('hue.global.info', { message: t('Changes saved!') });
        }
      }
    );
  };

  const handleDownload = () => {
    huePubSub.publish('hue.global.info', { message: t('Downloading your file, Please wait...') });
  };

  const fileDownloadUrl = `${DOWNLOAD_API_URL}?path=${fileStats.path}`;
  const filePreviewUrl = `${fileDownloadUrl}&&disposition=inline`;

  const isEditingEnabled =
    !error &&
    !isEditing &&
    config?.storage_browser.max_file_editor_size &&
    config?.storage_browser.max_file_editor_size > fileStats.size &&
    EDITABLE_FILE_FORMATS.has(fileType) &&
    !inTrash(fileStats.path);

  const pageStats = {
    pageNumber: pageNumber,
    totalPages: Math.ceil(fileStats.size / pageSize),
    pageSize: 0,
    totalSize: 0
  };

  const errorConfig = [
    {
      enabled: !!error && error.response?.status !== 422,
      message: t('An error occurred while fetching file content for path "{{path}}".', {
        path: fileStats.path
      }),
      actionText: t('Retry'),
      onClick: onReload
    }
  ];

  return (
    <>
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

        <LoadingErrorWrapper loading={loading || isSaving} errors={errorConfig} hideOnLoading>
          <div className="preview">
            <div className="preview__title-bar">
              {t('Content')}
              <div className="preview__action-group">
                {isEditingEnabled && (
                  <PrimaryButton data-testid="preview--edit--button" onClick={handleEdit}>
                    {t('Edit')}
                  </PrimaryButton>
                )}
                {isEditing && (
                  <>
                    <PrimaryButton
                      data-testid="preview--save--button"
                      onClick={handleSave}
                      disabled={fileContent === data?.contents}
                    >
                      {t('Save')}
                    </PrimaryButton>
                    <Button
                      role="button"
                      data-testid="preview--cancel--button"
                      onClick={handleCancel}
                    >
                      {t('Cancel')}
                    </Button>
                  </>
                )}
                {config?.storage_browser.enable_file_download_button && (
                  <a href={fileDownloadUrl}>
                    <PrimaryButton data-testid="preview--download--button" onClick={handleDownload}>
                      {t('Download')}
                    </PrimaryButton>
                  </a>
                )}
              </div>
            </div>

            <div className="preview__content">
              {error?.response?.status !== 422 && (
                <div className="preview__editable-file">
                  <textarea
                    value={fileContent}
                    onChange={e => setFileContent(e.target.value)}
                    readOnly={!isEditing}
                    className="preview__textarea"
                  />
                  {pageStats.totalPages > 1 && (
                    <Pagination setPageNumber={setPageNumber} pageStats={pageStats} />
                  )}
                </div>
              )}

              {(error?.response?.status === 422 || fileType === SupportedFileTypes.COMPRESSED) && (
                <div className="preview__unsupported">
                  {t('Preview is not available for this file. Please download the file instead.')}
                </div>
              )}

              {fileType === SupportedFileTypes.IMAGE && <img src={filePreviewUrl} alt={fileName} />}

              {fileType === SupportedFileTypes.DOCUMENT && (
                <div className="preview__document">
                  <div>
                    <PrimaryButton data-testid="" onClick={() => window.open(filePreviewUrl)}>
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
                  <track kind="captions" src="" srcLang="en" label="English" />
                </audio>
              )}

              {fileType === SupportedFileTypes.VIDEO && (
                <video controls preload="auto" data-testid="preview__content__video">
                  <source src={filePreviewUrl} />
                  {t('Your browser does not support the video element.')}
                  <track kind="captions" src="" srcLang="en" label="English" />
                </video>
              )}
            </div>
          </div>
        </LoadingErrorWrapper>
      </div>
    </>
  );
};

export default StorageFilePage;
