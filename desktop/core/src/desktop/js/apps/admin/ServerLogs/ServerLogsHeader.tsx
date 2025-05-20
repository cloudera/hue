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
import Input from 'cuix/dist/components/Input';
import Button from 'cuix/dist/components/Button';
import Search from '@cloudera/cuix-core/icons/react/SearchIcon';
import Download from '@cloudera/cuix-core/icons/react/DownloadIcon';
import { i18nReact } from '../../../utils/i18nReact';
import huePubSub from '../../../utils/huePubSub';
import './ServerLogsHeader.scss';

interface ServerLogsHeaderProps {
  onFilterChange: (value: string) => void;
  onWrapLogsChange: (wrap: boolean) => void;
  hostName: string;
}

const ServerLogsHeader: React.FC<ServerLogsHeaderProps> = ({
  onFilterChange,
  onWrapLogsChange,
  hostName
}): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [filterValue, setFilterValue] = useState('');
  const [wrapLogs, setWrapLogs] = useState(true);

  const handleFilterChange = (newFilterValue: string) => {
    setFilterValue(newFilterValue);
    onFilterChange(newFilterValue);
  };

  const handleDownloadClick = () => {
    huePubSub.publish('open.link', '/desktop/download_logs');
  };

  return (
    <div className="hue-server-admin-header admin-header">
      <Input
        className="server__input-filter"
        placeholder={t('Search in the logs')}
        prefix={
          <span className="server__input-filter--prefix">
            <Search />
          </span>
        }
        value={filterValue}
        onChange={e => handleFilterChange(e.target.value)}
      />

      <div className="server--right-actions">
        <span className="server__host-text">{`${t('Host:')} ${hostName}`}</span>
        <Input
          type="checkbox"
          onChange={e => {
            setWrapLogs(e.target.checked);
            onWrapLogsChange(e.target.checked);
          }}
          checked={wrapLogs}
          className="server__checkbox-icon"
          id="wrapLogsToggle"
        />
        <label className="server__wrap-logs" htmlFor="wrapLogsToggle">
          {t('Wrap logs')}
        </label>

        <Button
          className="server__download-button"
          icon={<Download />}
          onClick={handleDownloadClick}
        >
          {t('Download entire log as zip')}
        </Button>
      </div>
    </div>
  );
};

export default ServerLogsHeader;
