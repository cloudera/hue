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
import { Alert, Form } from 'antd';
import { i18nReact } from '../../../../utils/i18nReact';
import { useDataCatalog } from '../../../../utils/hooks/useDataCatalog/useDataCatalog';
import { DestinationConfig } from '../../types';

import './DestinationSettings.scss';
import FormInput, { FieldType } from '../../../../reactComponents/FormInput/FormInput';

interface DestinationSettingsProps {
  defaultValues: DestinationConfig;
  onChange: (name: string, value: string) => void;
}

const DestinationSettings = ({
  defaultValues,
  onChange
}: DestinationSettingsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [error, setError] = React.useState<{
    tableName?: string;
  }>({});
  const [tableName, setTableName] = React.useState<string | undefined>(defaultValues?.tableName);

  const {
    loading,
    databases,
    database,
    connectors,
    connector,
    computes,
    compute,
    tables,
    setCompute,
    setConnector,
    setDatabase
  } = useDataCatalog();

  const inputConfig = [
    {
      label: t('Engine'),
      name: 'connectorId',
      type: FieldType.SELECT,
      tooltip: t('Select the engine to use for the destination'),
      options: connectors.map(connector => ({
        label: connector.displayName,
        value: connector.id
      }))
    },
    {
      label: t('Compute'),
      name: 'computeId',
      type: FieldType.SELECT,
      tooltip: t('Select the compute to use for the destination'),
      options:
        computes?.map(compute => ({
          label: compute.name,
          value: compute.id
        })) ?? [],
      hidden: computes?.length === 1
    },
    {
      label: t('Database'),
      name: 'database',
      type: FieldType.SELECT,
      tooltip: t('Select the database to use for the destination'),
      options:
        databases?.map(database => ({
          label: database,
          value: database
        })) ?? []
    },
    {
      label: t('Table Name'),
      name: 'tableName',
      type: FieldType.INPUT,
      tooltip: t('Enter the name of the table to use for the destination')
    }
  ].filter(({ hidden }) => !hidden);

  const handleDropdownChange = (name: string, value: string) => {
    if (name === 'connectorId') {
      const selectedConnector = connectors?.find(connector => connector.id === value);
      if (selectedConnector) {
        setConnector(selectedConnector);
      }
    } else if (name === 'computeId') {
      const selectedCompute = computes?.find(compute => compute.id === value);
      if (selectedCompute) {
        setCompute(selectedCompute);
      }
    } else if (name === 'database') {
      setDatabase(value);
    } else if (name === 'tableName') {
      setTableName(value);
    }

    onChange(name, value);
  };

  const validateTableName = (name: string) => {
    const tableExists = tables?.some(table => table.name.toLowerCase() === name.toLowerCase());
    if (tableExists) {
      setError(prev => ({ ...prev, tableName: t('Table name already exists in the database') }));
    } else {
      setError(prev => ({ ...prev, tableName: undefined }));
    }
  };

  useEffect(() => {
    if (!connectors?.length) {
      return;
    }

    if (defaultValues?.connectorId) {
      const selectedConnector = connectors.find(conn => conn.id === defaultValues.connectorId);
      if (selectedConnector) {
        setConnector(selectedConnector);
      }
    } else {
      setConnector(connectors[0]);
      onChange('connectorId', connectors[0].id);
    }
  }, [connectors, defaultValues?.connectorId]);

  useEffect(() => {
    if (!databases?.length) {
      return;
    }

    if (defaultValues?.database) {
      const selectedDatabase = databases.find(db => db === defaultValues.database);
      if (selectedDatabase) {
        setDatabase(selectedDatabase);
      }
    } else if (!defaultValues?.database) {
      setDatabase(databases[0]);
      onChange('database', databases[0]);
    }
  }, [databases, defaultValues?.database]);

  useEffect(() => {
    if (!computes?.length) {
      return;
    }

    if (defaultValues?.computeId) {
      const selectedCompute = computes.find(comp => comp.id === defaultValues.computeId);
      if (selectedCompute) {
        setCompute(selectedCompute);
      }
    } else if (!compute) {
      setCompute(computes[0]);
      onChange('computeId', computes[0].id);
    }
  }, [computes, defaultValues?.computeId]);

  useEffect(() => {
    if (defaultValues?.tableName && defaultValues.tableName !== tableName) {
      setTableName(defaultValues.tableName);
    }
  }, [defaultValues?.tableName]);

  useEffect(() => {
    if (tableName) {
      validateTableName(tableName);
    }
  }, [tableName, tables]);

  const selectedSettings: DestinationConfig = {
    connectorId: connector?.id,
    computeId: compute?.id,
    database: database,
    tableName: tableName
  };

  const loadingState = {
    connectorId: loading.connector,
    computeId: loading.compute,
    database: loading.database,
    tableName: loading.table
  };

  return (
    <div className="importer-destination-settings">
      {error && Object.values(error).some(Boolean) && (
        <Alert message={error.tableName} type="error" showIcon />
      )}
      <div className="importer-destination-settings__form-container">
        {inputConfig.map(field => (
          <Form key={field.name} layout="vertical">
            <FormInput<string, DestinationConfig>
              field={field}
              defaultValue={selectedSettings[field.name]}
              value={selectedSettings[field.name]}
              onChange={handleDropdownChange}
              className="importer-destination-settings__input"
              loading={loadingState[field.name]}
              error={error[field.name]}
            />
          </Form>
        ))}
      </div>
    </div>
  );
};

export default DestinationSettings;
