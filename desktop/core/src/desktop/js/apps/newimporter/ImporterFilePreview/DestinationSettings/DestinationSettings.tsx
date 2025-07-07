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

import React, { useEffect } from 'react';
import { Form, Input, Select } from 'antd';
import { i18nReact } from '../../../../utils/i18nReact';
import { useDataCatalog } from '../../../../utils/hooks/useDataCatalog/useDataCatalog';
import { DestinationConfig } from '../../types';

import './DestinationSettings.scss';

interface DestinationSettingsProps {
  defaultValues: DestinationConfig;
  onChange: (name: string, value: string) => void;
}

const DestinationSettings = ({
  defaultValues,
  onChange
}: DestinationSettingsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [tableName, setTableName] = React.useState<string | undefined>(defaultValues?.tableName);

  const {
    loading,
    databases,
    database,
    connectors,
    connector,
    computes,
    compute,
    setCompute,
    setConnector,
    setDatabase
  } = useDataCatalog();

  const inputConfig = [
    {
      label: t('Engine'),
      name: 'engine',
      type: 'select',
      options: connectors.map(connector => ({
        label: connector.displayName,
        value: connector.id
      }))
    },
    {
      label: t('Compute'),
      name: 'compute',
      type: 'select',
      options: computes?.map(compute => ({
        label: compute.name,
        value: compute.id
      })),
      hidden: computes?.length === 1
    },
    {
      label: t('Database'),
      name: 'database',
      type: 'select',
      options: databases?.map(database => ({
        label: database,
        value: database
      }))
    },
    {
      label: t('Table Name'),
      name: 'tableName',
      type: 'input'
    }
  ].filter(({ hidden }) => !hidden);

  const handleDropdownChange = (name: string, value: string) => {
    if (name === 'engine') {
      const selectedConnector = connectors?.find(connector => connector.id === value);
      if (selectedConnector) {
        setConnector(selectedConnector);
      }
    } else if (name === 'database') {
      const selectedDatabase = databases?.find(database => database === value);
      if (selectedDatabase) {
        setDatabase(selectedDatabase);
      }
    } else if (name === 'compute') {
      const selectedCompute = computes?.find(compute => compute.id === value);
      if (selectedCompute) {
        setCompute(selectedCompute);
      }
    }

    onChange(name, value);
  };

  const handleTableChange = (value: string) => {
    setTableName(value);
  };

  useEffect(() => {
    if (defaultValues?.connectorId && connectors?.length) {
      const selectedConnector = connectors.find(conn => conn.id === defaultValues.connectorId);
      if (selectedConnector) {
        setConnector(selectedConnector);
      }
    }
    if (defaultValues?.database && databases?.length) {
      const selectedDatabase = databases.find(db => db === defaultValues.database);
      if (selectedDatabase) {
        setDatabase(selectedDatabase);
      }
    }
    if (defaultValues?.computeId && computes?.length) {
      const selectedCompute = computes.find(comp => comp.id === defaultValues.computeId);
      if (selectedCompute) {
        setCompute(selectedCompute);
      }
    }
  }, [defaultValues, connectors, databases, computes, setConnector, setDatabase, setCompute]);

  const selectedSettings = {
    engine: connector?.id,
    compute: compute?.id,
    database: database,
    tableName: tableName
  };

  return (
    <div className="importer-destination-settings">
      {inputConfig.map(({ label, name, type, options }) => {
        if (type === 'select') {
          return (
            <Form layout="vertical" key={name}>
              <Form.Item key={name} label={label} htmlFor={name}>
                <Select
                  getPopupContainer={triggerNode => triggerNode.parentElement}
                  options={options}
                  id={name}
                  loading={loading}
                  value={selectedSettings[name]}
                  className="importer-destination-settings__select-dropdown"
                  onChange={value => handleDropdownChange(name, value)}
                />
              </Form.Item>
            </Form>
          );
        }
        if (type === 'input') {
          return (
            <Form layout="vertical" key={name}>
              <Form.Item key={name} label={label} htmlFor={name}>
                <Input
                  id={name}
                  value={tableName}
                  className="importer-destination-settings__input"
                  onChange={e => handleTableChange(e.target.value)}
                />
              </Form.Item>
            </Form>
          );
        }
        return <></>;
      })}
    </div>
  );
};

export default DestinationSettings;
