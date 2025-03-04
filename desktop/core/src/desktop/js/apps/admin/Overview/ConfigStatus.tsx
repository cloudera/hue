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

// Assuming you have an API endpoint for `install_app_examples`

import React from 'react';
import { Spin, Alert, Table } from 'antd';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { INSTALL_APP_EXAMPLES_API_URL } from '../Components/utils';
import { i18nReact } from '../../../utils/i18nReact';
import './Overview.scss';

function ConfigStatus(): JSX.Element {
  const { t } = i18nReact.useTranslation();
  const {
    data: installData,
    loading,
    error
    // reloadData
  } = useLoadData(INSTALL_APP_EXAMPLES_API_URL);

  const columns = [
    {
      dataIndex: 'name',
      key: 'name',
      render: name => <span className="config-table-name">{name}</span>
    },
    {
      key: 'details',
      render: record => (
        <div>
          {record.value && (
            <p>
              {t('Current value')}: <span className="config-table-name">{record.value}</span>
            </p>
          )}
          <p>{record.message}</p>
        </div>
      )
    }
  ];

  if (error) {
    return (
      <div>
        <Alert
          message={t(`Error: ${error}`)}
          description={t('An error occurred while attempting to install app examples.')}
          type="error"
        />
      </div>
    );
  }

  if (loading) {
    return <Spin spinning={loading}>{t('Installing app examples...')}</Spin>;
  }

  const openConfigDocs = () => {
    window.open('https://docs.gethue.com/administrator/configuration/', '_blank');
  };

  return (
    <>
      <div className="config-status">
        <h1>{t('Checking current configuration')}</h1>
        {installData && installData['hue_config_dir'] && (
          <div>
            {t('Configuration files located in:')}{' '}
            <span className="config__address-value">{installData['hue_config_dir']}</span>
          </div>
        )}

        {installData &&
          installData['config_error_list'] &&
          installData['config_error_list'].length > 0 && (
            <Alert
              message={
                <span>
                  <a className="config-link" onClick={openConfigDocs}>
                    {t('Potential misconfiguration detected.')}
                  </a>{' '}
                  {t('Fix and restart Hue.')}
                </span>
              }
              type="warning"
              className="config__alert-margin"
            />
          )}

        {installData &&
          installData['config_error_list'] &&
          installData['config_error_list'].length > 0 && (
            <Table
              dataSource={installData['config_error_list']}
              columns={columns}
              rowKey="name"
              pagination={false}
              showHeader={false}
            />
          )}
      </div>
    </>
  );
}

export default ConfigStatus;
