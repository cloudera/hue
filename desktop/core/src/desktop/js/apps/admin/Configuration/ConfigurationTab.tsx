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
import { Spin } from 'antd';
import { i18nReact } from '../../../utils/i18nReact';
import './Configuration.scss';
import { DEFAULT_SELECTED_APP, GET_CONFIG_API } from './utils';
import FilterSelect from '../AdminHeader';
import { ConfigurationValue } from './ConfigurationValue';
import { ConfigurationKey } from './ConfigurationKey';


interface App {
  name: string;
  has_ui: boolean;
  display_name: string;
}

export interface ConfigValue {
  help: string;
  key: string;
  is_anonymous: boolean;
  values?: ConfigValue[];
  default?: string;
  value?: string;
}

interface Config {
  help: string;
  key: string;
  is_anonymous: boolean;
  values: ConfigValue[];
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
  const [selectedApp, setSelectedApp] = useState<string>(DEFAULT_SELECTED_APP);
  const [filter, setFilter] = useState<string>('');

  useEffect(() => {
    const fetchHueConfig = async () => {
      try {
        const response = await fetch(GET_CONFIG_API);
        const data: HueConfig = await response.json();
        setHueConfig(data);
        if (data.apps.find(app => app.name === 'desktop')) {
          setSelectedApp('desktop');
        }
      } catch (error) {
        console.error('Fetch error:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchHueConfig();
  }, []);


  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilter(e.target.value.toLowerCase());
  };

  const filterConfig = (config: ConfigValue, lowerCaseFilter: string): ConfigValue | undefined => {
    if (
      (config.key && config.key.toLowerCase().includes(lowerCaseFilter)) ||
      (config.help && config.help.toLowerCase().includes(lowerCaseFilter)) ||
      (!config.is_anonymous && config.key.toLowerCase().includes(lowerCaseFilter))
    ) {
      return config;
    }

    if (config.values) {
      const values = config.values
        .map(val => filterConfig(val, lowerCaseFilter))
        .filter(Boolean) as ConfigValue[];
      if (values.length) {
        return { ...config, values };
      }
    }
  };

  const filteredConfig = useMemo (() => {
    return hueConfig?.config
    ?.map(config => filterConfig(config, filter))
    .filter(Boolean) as Config[];
  }, [hueConfig, filter]);

  const selectedConfig = useMemo(() => {
    return filteredConfig?.find(config => config.key === selectedApp);
  }, [filteredConfig, selectedApp]);

  return (
    <div className="cuix antd config-component">
      <Spin spinning={loading}>
        <div className="config-section-header">Sections</div>

          <FilterSelect
            options={hueConfig?.apps.map(app => app.name) || []}
            selectedValue={selectedApp}
            onSelectChange={setSelectedApp}
            filterValue={filter}
            onFilterChange={handleFilterChange}
            placeholder={`Filter in ${selectedApp}...`}
            configAddress={hueConfig?.conf_dir}
          />

        {selectedApp &&
          selectedConfig &&
          (selectedConfig.values.length > 0 ? (
            <div>
              {selectedConfig.values.map((record, index) => (
                <div key={index} className="main-config-item">
                  <ConfigurationKey record={record} />
                  <ConfigurationValue record={record} />
                </div>
              ))}
            </div>
          ) : (
            <i>{t('Empty configuration section')}</i>
          ))}

      </Spin>
    </div>
  );
};

export default Configuration;
