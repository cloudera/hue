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
import ServerLogsHeader from './ServerLogsHeader';
import { i18nReact } from '../../../utils/i18nReact';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import LoadingErrorWrapper from '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';
import HighlightText from '../Components/HighlightText';
import { SERVER_LOGS_API_URL } from '../Components/utils';
import './ServerLogsTab.scss';

interface ServerLogsData {
  logs: string[];
  hueHostname: string;
}

const ServerLogs: React.FC = (): JSX.Element => {
  const [filter, setFilter] = useState<string>('');
  const [wrapLogs, setWrapLogs] = useState(true);
  const { t } = i18nReact.useTranslation();
  const { data, loading, error, reloadData } = useLoadData<ServerLogsData>(SERVER_LOGS_API_URL, {
    params: {
      reverse: true
    }
  });

  const errors = [
    {
      enabled: !!error,
      message: t('An error occurred while fetching server logs.'),
      actionText: t('Retry'),
      onClick: reloadData
    }
  ];

  const isEmptyLogs = !data?.logs || !data?.logs?.some(log => log.length);

  return (
    <div className="hue-server-logs-component">
      <LoadingErrorWrapper loading={loading} errors={errors}>
        <ServerLogsHeader
          onFilterChange={setFilter}
          onWrapLogsChange={setWrapLogs}
          hostName={data?.hueHostname ?? ''}
        />
        {isEmptyLogs ? (
          <pre className="server__no-logs-found">No logs found!</pre>
        ) : (
          <div className="server__display-logs">
            {data.logs.map((line, index) => (
              <div
                className={`server__log-line ${wrapLogs ? 'server__log-line--wrap' : ''}`}
                key={'logs_' + index}
              >
                <HighlightText text={line} searchValue={filter} />
              </div>
            ))}
          </div>
        )}
      </LoadingErrorWrapper>
    </div>
  );
};

export default ServerLogs;
