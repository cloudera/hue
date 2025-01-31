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

import React, { useState } from 'react';
import { Spin, Alert } from 'antd';
import ServerLogsHeader from './ServerLogsHeader';
import { i18nReact } from '../../../utils/i18nReact';
import useLoadData from '../../../utils/hooks/useLoadData';
import HighlightText from '../Components/HighlightText';
import { SERVER_LOGS_API_URL } from '../Components/utils';
import './ServerLogsTab.scss';

interface ServerLogsData {
  logs: string[];
  hue_hostname: string;
}

const ServerLogs: React.FC = (): JSX.Element => {
  const [filter, setFilter] = useState<string>('');
  const [wrapLogs, setWrapLogs] = useState(true);
  const { t } = i18nReact.useTranslation();

  const { data: logsData, loading, error } = useLoadData<ServerLogsData>(SERVER_LOGS_API_URL);

  if (error) {
    return (
      <div className="server-logs-component">
        <Alert
          message={t(`Error: ${error}`)}
          description={t('An error occurred while fetching server logs.')}
          type="error"
        />
      </div>
    );
  }

  return (
    <div className="hue-server-logs-component">
      <Spin spinning={loading}>
        {!loading && (
          <>
            <ServerLogsHeader
              onFilterChange={setFilter}
              onWrapLogsChange={setWrapLogs}
              hostName={logsData?.hue_hostname ?? ''}
            />
            {logsData && (logsData.logs.length === 0 || logsData.logs[0] === '') && (
              <pre className="server__no-logs-found">No logs found!</pre>
            )}

            {logsData && logsData.logs.length > 0 && logsData.logs[0] !== '' && (
              <div className="server__display-logs">
                {logsData.logs.map((line, index) => (
                  <div
                    className={`server__log-line ${wrapLogs ? 'server_wrap' : ''}`}
                    key={'logs_' + index}
                  >
                    <HighlightText text={line} searchValue={filter} />
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </Spin>
    </div>
  );
};

export default ServerLogs;
