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

import React from 'react';
import { useDropzone } from 'react-dropzone';
import ImportIcon from '@cloudera/cuix-core/icons/react/ImportIcon';
import './DragAndDrop.scss';
import { i18nReact } from '../../utils/i18nReact';

interface DragAndDropProps {
  onDrop: (files: File[]) => void;
  children?: JSX.Element;
}

const DragAndDrop = ({ children, onDrop }: DragAndDropProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    noClick: !!children
  });

  return (
    <div className="drag-drop">
      <div {...getRootProps()} className="drag-drop__dropzone">
        <input {...getInputProps()} className="drag-drop__input" data-testid="drag-drop__input" />
        {isDragActive && <div className="drag-drop__message">{t('Drop files here')}</div>}
        {!isDragActive && !children && (
          <div className="drag-drop__message">
            <div className="drag-drop__message__select-file">
              <ImportIcon /> {t('Select files')}
            </div>
            <div>{t('Drag and Drop files or browse')}</div>
          </div>
        )}
        {!isDragActive && children}
      </div>
    </div>
  );
};

export default DragAndDrop;
