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

const StorageFilePage = ({ fileData }: { fileData: PathAndFileData }): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [isEditing, setIsEditing] = React.useState(false);
  const [fileContent, setFileContent] = React.useState(fileData.view?.contents);
  const fileMetaData = useMemo(() => getFileMetaData(t, fileData), [t, fileData]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    // TODO: Save file content to API
    setIsEditing(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFileContent(fileData.view?.contents);
  };

  return (
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
            <PrimaryButton
              data-testid="preview--edit--button"
              data-event=""
              onClick={handleEdit}
              hidden={isEditing}
            >
              {t('Edit')}
            </PrimaryButton>
            <PrimaryButton
              data-testid="preview--save--button"
              data-event=""
              onClick={handleSave}
              disabled={fileContent === fileData.view?.contents}
              hidden={!isEditing}
            >
              {t('Save')}
            </PrimaryButton>
            <Button
              role="button"
              data-testid="preview--cancel--button"
              data-event=""
              onClick={handleCancel}
              hidden={!isEditing}
            >
              {t('Cancel')}
            </Button>
          </div>
        </div>

        <textarea
          data-testid="file-content"
          value={fileContent}
          onChange={e => setFileContent(e.target.value)}
          readOnly={!isEditing}
          className="preview__textarea"
        />
      </div>
    </div>
  );
};

export default StorageFilePage;
