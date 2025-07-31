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
import Select from 'cuix/dist/components/Select/Select';
import ConfigureIcon from '@cloudera/cuix-core/icons/react/ConfigureIcon';
import { i18nReact } from '../../../../utils/i18nReact';
import { sourceConfigs } from '../../constants';
import { CombinedFileFormat, FileFormatResponse } from '../../types';

import './SourceConfiguration.scss';

interface SourceConfigurationProps {
  fileFormat?: FileFormatResponse;
  setFileFormat: (format: FileFormatResponse) => void;
}
const SourceConfiguration = ({
  fileFormat,
  setFileFormat
}: SourceConfigurationProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const onChange = (value: string | number | boolean, name: keyof CombinedFileFormat) => {
    if (fileFormat) {
      setFileFormat({
        ...fileFormat,
        [name]: value
      });
    }
  };

  return (
    <details className="hue-importer-configuration">
      <summary className="hue-importer-configuration__summary">
        <ConfigureIcon />
        {t('Configure source')}
      </summary>
      <div className="hue-importer-configuration-options">
        {sourceConfigs
          .filter(config => !config.hidden?.(fileFormat?.type))
          .map(config => (
            <div key={config.name}>
              <label htmlFor={config.name}>{t(config.label)}</label>
              <Select
                bordered={true}
                className="hue-importer-configuration__dropdown"
                id={config.name}
                options={config.options}
                onChange={value => onChange(value, config.name)}
                value={fileFormat?.[config.name]}
                getPopupContainer={triggerNode => triggerNode.parentElement}
              />
            </div>
          ))}
      </div>
    </details>
  );
};

export default SourceConfiguration;
