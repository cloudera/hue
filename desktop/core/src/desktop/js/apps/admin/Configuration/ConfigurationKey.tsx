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
import { Tooltip } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { ConfigValue } from './ConfigurationTab';
import './Configuration.scss';

export const ConfigurationKey: React.FC<{ record: ConfigValue }> = ({ record }) => {
  if (record.is_anonymous) {
    return (
      <div>
        Default section
        {record.help && (
          <Tooltip title={record.help}>
            <InfoCircleOutlined className="config-tooltip" />
          </Tooltip>
        )}
      </div>
    );
  }
  if (record?.values) {
    return (
      <span>
        <span className="main-config-item-heading">{record.key}</span>
        {record.help && (
          <Tooltip title={record.help}>
            <InfoCircleOutlined className="config-tooltip" />
          </Tooltip>
        )}
      </span>
    );
  } else {
    return (
      <span>
        <span className="last-config-heading">{record.key}</span>
        {record.value && <span className="config-value">{record.value}</span>}
        <div>
          <span className="last-config-helpText">{record.help}</span>
          <span className="last-config-key">
            {record.default && <span className="default-value">Default: {record.default}</span>}
          </span>
        </div>
      </span>
    );
  }
};
