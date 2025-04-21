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
import { i18nReact } from '../../../../utils/i18nReact';
import ConfigureIcon from '@cloudera/cuix-core/icons/react/ConfigureIcon';
import ColumnModalTable from './ColumnModalTable';
import '../SourceConfiguration/SourceConfiguration.scss';

const ColumnModal = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [isOpen, setIsOpen] = useState(false);

  const handleClose = () => {
    setIsOpen(false);
  };

  return (
    <div className="hue-importer-columnmodal">
      <summary className="hue-importer-columnmodal__button" onClick={() => setIsOpen(true)}>
        <ConfigureIcon />
        {t('Edit Columns')}
      </summary>
      <ColumnModalTable isOpen={isOpen} closeModal={handleClose} />
    </div>
  );
};

export default ColumnModal;
