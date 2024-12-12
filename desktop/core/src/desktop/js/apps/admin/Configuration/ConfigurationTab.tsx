// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, { useState, useEffect, useMemo } from 'react';
import { Spin, Alert } from 'antd';
import { i18nReact } from '../../../utils/i18nReact';
import AdminHeader from '../AdminHeader';
import { ConfigurationValue } from './ConfigurationValue';
import { ConfigurationKey } from './ConfigurationKey';
import ApiHelper from '../../../api/apiHelper';
import './Configuration.scss';

interface App {
  name: string;
  has_ui: boolean;
  display_name: string;
}

export interface AdminConfigValue {
  help: string;
  key: string;
  is_anonymous: boolean;
  values?: AdminConfigValue[];
  default?: string;
  value?: string;
}

interface Config {
  help: string;
  key: string;
  is_anonymous: boolean;
  values: AdminConfigValue[];
}

interface HueConfig {
  apps: App[];
  config: Config[];
  conf_dir: string;
}

const Configuration: React.FC = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [hueConfig, setHueConfig] = useState<HueConfig>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [selectedApp, setSelectedApp] = useState<string>('desktop');
  const [filter, setFilter] = useState<string>('');

  useEffect(() => {
    ApiHelper.fetchHueConfigAsync()
      .then(data => {
        setHueConfig(data);
        if (data.apps.find(app => app.name === 'desktop')) {
          setSelectedApp('desktop');
        }
      })
      .catch(error => {
        setError(error.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const filterConfig = (
    config: AdminConfigValue,
    lowerCaseFilter: string
  ): AdminConfigValue | undefined => {
    //Filtering is done on Key and Help only
    const keyMatches = config.key?.toLowerCase().includes(lowerCaseFilter);
    const helpMatches = config.help?.toLowerCase().includes(lowerCaseFilter);

    if (keyMatches || helpMatches) {
      return config;
    }

    if (config.values) {
      const filteredValues = config.values
        .map(val => filterConfig(val, lowerCaseFilter))
        .filter(Boolean) as AdminConfigValue[];
      if (filteredValues.length) {
        return { ...config, values: filteredValues };
      }
    }
    return undefined;
  };

  const selectedConfig = useMemo(() => {
    const filterSelectedApp = hueConfig?.config?.find(config => config.key === selectedApp);

    return filterSelectedApp?.values
      .map(config => filterConfig(config, filter.toLowerCase()))
      .filter(Boolean) as Config[];
  }, [hueConfig, filter, selectedApp]);

  return (
    <div className="config-component">
      <Spin spinning={loading}>
        {error && (
          <Alert
            message={`Error: ${error}`}
            description="Error in displaying the Configuration!"
            type="error"
          />
        )}

        {!error && (
          <>
            <div className="config__section-header">Sections</div>
            <AdminHeader
              options={hueConfig?.apps.map(app => app.name) || []}
              selectedValue={selectedApp}
              onSelectChange={setSelectedApp}
              filterValue={filter}
              onFilterChange={setFilter}
              placeholder={`Filter in ${selectedApp}...`}
              configAddress={hueConfig?.conf_dir}
            />
            {selectedApp &&
              selectedConfig &&
              (selectedConfig.length > 0 ? (
                <>
                  {selectedConfig.map((record, index) => (
                    <div key={index} className="config__main-item">
                      <ConfigurationKey record={record} />
                      <ConfigurationValue record={record} />
                    </div>
                  ))}
                </>
              ) : (
                <i>{t('Empty configuration section')}</i>
              ))}
          </>
        )}
      </Spin>
    </div>
  );
};

export default Configuration;
