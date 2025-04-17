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

import React from 'react';
import Loading from 'cuix/dist/components/Loading';
import Alert from 'cuix/dist/components/Alert';
import Table from 'cuix/dist/components/Table';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { CHECK_CONFIG_EXAMPLES_API_URL } from '../Components/utils';
import { HUE_DOCS_CONFIG_URL } from '../Components/utils';
import { i18nReact } from '../../../utils/i18nReact';
import './Overview.scss';

interface ConfigError {
  name: string;
  message: string;
}
interface CheckConfigResponse {
  hueConfigDir: string;
  configErrors: ConfigError[];
}

const ConfigStatus = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const { data, loading, error } = useLoadData<CheckConfigResponse>(CHECK_CONFIG_EXAMPLES_API_URL);

  const columns = [
    {
      dataIndex: 'name',
      render: name => <span className="config__table-name">{name}</span>
    },
    {
      key: 'details',
      render: record => (
        <div>
          {record.value && (
            <p>
              {t('Current value')}: <span className="config__table-value">{record.value}</span>
            </p>
          )}
          <p>{record.message}</p>
        </div>
      )
    }
  ];

  const configErrorsExist = Boolean(data?.configErrors?.length);

  return (
    <div className="overview-config">
      {loading && <Loading spinning={loading} className="config__spin" />}
      {error && (
        <Alert
          message={`${t('Error:')} ${error}`}
          description={t('An error occurred while attempting to load the configuration status.')}
          type="error"
        />
      )}
      {!loading && !error && (
        <>
          <h1>{t('Checking current configuration')}</h1>
          {data?.hueConfigDir && (
            <div>
              {t('Configuration files located in: ')}
              <span className="config__address-value">{data['hueConfigDir']}</span>
            </div>
          )}

          {configErrorsExist && data ? (
            <>
              <Alert
                message={
                  <span>
                    <a href={HUE_DOCS_CONFIG_URL} target="_blank" className="config__link">
                      {t('Potential misconfiguration detected.')}
                    </a>{' '}
                    {t('Fix and restart Hue.')}
                  </span>
                }
                type="warning"
                className="config__alert-margin"
              />

              <Table
                dataSource={data.configErrors}
                columns={columns}
                rowKey={record => `${record.name}-${record.message.slice(1, 50)}`}
                pagination={false}
                showHeader={false}
              />
            </>
          ) : (
            <Alert
              message={t('All OK. Configuration check passed.')}
              type="success"
              className="config__alert-margin"
            />
          )}
        </>
      )}
    </div>
  );
};

export default ConfigStatus;
