// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import React from 'react';
import Loading from 'cuix/dist/components/Loading';
import DescriptionList, { DescriptionListItem } from 'cuix/dist/components/DescriptionList';
import { i18nReact } from '../../../utils/i18nReact';
import './DatabaseProperties.scss';

export interface DatabaseProperties {
  owner_name?: string;
  owner_type?: string;
  location?: string;
  hdfs_link?: string;
  parameters?: string;
}

export interface DatabasePropertiesProps {
  properties?: DatabaseProperties;
  loading?: boolean;
}

const DatabasePropertiesComponent = ({
  properties,
  loading
}: DatabasePropertiesProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  return (
    <div className="hue-database-properties">
      <h3 className="hue-database-properties__title">{t('Properties')}</h3>
      <Loading spinning={!!loading}>
        <DescriptionList layout="inline" upperCaseLabel>
          <DescriptionListItem label={t('Owner')}>
            {properties?.owner_name ? (
              <>
                {properties.owner_name}
                {properties.owner_type && (
                  <span className="hue-database-properties__property-type">
                    ({properties.owner_type})
                  </span>
                )}
              </>
            ) : (
              <span className="hue-database-properties__property-empty">{t('None')}</span>
            )}
          </DescriptionListItem>
          {properties?.location && (
            <DescriptionListItem label={t('Location')}>
              {properties.hdfs_link ? (
                <a
                  href={properties.hdfs_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hue-database-properties__property-link"
                >
                  {t('location')}
                </a>
              ) : (
                <span className="hue-database-properties__property-path">
                  {properties.location}
                </span>
              )}
            </DescriptionListItem>
          )}
          {properties?.parameters && (
            <DescriptionListItem label={t('Parameters')}>
              <div className="hue-database-properties__parameters">{properties.parameters}</div>
            </DescriptionListItem>
          )}
        </DescriptionList>
      </Loading>
    </div>
  );
};

export default DatabasePropertiesComponent;
