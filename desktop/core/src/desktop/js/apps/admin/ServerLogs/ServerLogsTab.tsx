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

import React, { useState, useEffect } from 'react';
import { Spin, Alert } from 'antd';
import ServerLogsHeader from './ServerLogsHeader';
import { i18nReact } from '../../../utils/i18nReact';
import useLoadData from '../../../utils/hooks/useLoadData';
import './ServerLogsTab.scss';

interface ServerLogsData {
  logs: string[];
  hue_hostname: string;
}

const ServerLogs: React.FC = (): JSX.Element => {
  const [filter, setFilter] = useState<string>('');
  const [wrapLogs, setWrapLogs] = useState(true);
  const { t } = i18nReact.useTranslation();

  const {
    data: logsData,
    loading,
    error
    //reloadData
  } = useLoadData<ServerLogsData>('/api/v1/logs');

  useEffect(() => {
    const updateSize = () => {
      const newHeight = document.documentElement.clientHeight - 250;
      const logsComponent = document.querySelector('.server__display-logs') as HTMLElement;
      if (logsComponent) {
        logsComponent.style.height = `${newHeight}px`;
      }
    };
    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  const highlightText = (text: string, searchValue: string) => {
    if (!searchValue) {
      return text;
    }
    const regex = new RegExp(`(${searchValue})`, 'gi');
    const parts = text.split(regex);
    return parts.map((part, index) =>
      regex.test(part) ? (
        <mark key={'parts_' + index} className="server--highlight-word">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  if (error) {
    return (
      <div className="server-logs-component">
        <Alert
          message={t(`Error: ${error}`)}
          description="An error occurred while fetching server logs."
          type="error"
        />
      </div>
    );
  }

  return (
    <div className="server-logs-component">
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
                    {highlightText(line, filter)}
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
