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
import Loading from 'cuix/dist/components/Loading';
import Alert from 'cuix/dist/components/Alert';
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

interface VisualSection {
  header: string;
  content: Array<AdminConfigValue>;
}

const Configuration: React.FC = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [hueConfig, setHueConfig] = useState<HueConfig>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [selectedSection, setSelectedSection] = useState<string>('desktop');
  const [filter, setFilter] = useState<string>('');

  const ALL_SECTIONS_OPTION = t('ALL');

  useEffect(() => {
    ApiHelper.fetchHueConfigAsync()
      .then(data => {
        setHueConfig(data);
        if (data.apps.find(app => app.name === 'desktop')) {
          setSelectedSection('desktop');
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

  const visualSections = useMemo(() => {
    const showAllSections = selectedSection === ALL_SECTIONS_OPTION;
    const selectedFullConfigs = !hueConfig?.config
      ? []
      : showAllSections
        ? hueConfig.config
        : hueConfig.config.filter(config => config.key === selectedSection);

    return selectedFullConfigs
      .map(selectedSection => ({
        header: selectedSection.key,
        content: selectedSection.values
          .map(config => filterConfig(config, filter.toLowerCase()))
          .filter(Boolean) as Config[]
      }))
      .filter(headerContentObj => !!headerContentObj.content) as Array<VisualSection>;
  }, [hueConfig, filter, selectedSection]);

  const renderVisualSection = (visualSection: VisualSection) => {
    const showingMultipleSections = selectedSection === ALL_SECTIONS_OPTION;
    const content = visualSection.content;
    return content.length > 0 ? (
      <>
        {showingMultipleSections && (
          <h4 className="config__section-header">{visualSection.header}</h4>
        )}
        {content.map((record, index) => (
          <div key={index} className="config__main-item">
            <ConfigurationKey record={record} />
            <ConfigurationValue record={record} />
          </div>
        ))}
      </>
    ) : (
      !showingMultipleSections && <i>{t('Empty configuration section')}</i>
    );
  };

  const optionsIncludingAll = [
    ALL_SECTIONS_OPTION,
    ...(hueConfig?.apps.map(app => app.name) || [])
  ];

  return (
    <div className="config-component">
      <Loading spinning={loading}>
        {error && (
          <Alert
            message={`Error: ${error}`}
            description={t('Error in displaying the Configuration!')}
            type="error"
          />
        )}

        {!error && (
          <>
            <div className="config__section-dropdown-label">{t('Sections')}</div>
            <AdminHeader
              options={optionsIncludingAll}
              selectedValue={selectedSection}
              onSelectChange={setSelectedSection}
              filterValue={filter}
              onFilterChange={setFilter}
              placeholder={
                selectedSection === ALL_SECTIONS_OPTION
                  ? t('Filter...')
                  : `${t('Filter in')} ${selectedSection}...`
              }
              configAddress={hueConfig?.conf_dir}
            />
            {selectedSection &&
              visualSections?.length &&
              visualSections.map(visualSection => (
                <div key={visualSection.header}>{renderVisualSection(visualSection)}</div>
              ))}
          </>
        )}
      </Loading>
    </div>
  );
};

export default Configuration;
