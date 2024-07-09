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
import { ConfigValue as ParentConfigValue } from './ConfigurationTab';
import './Configuration.scss';
import { ConfigurationKey } from './ConfigurationKey';

export const ConfigurationValue: React.FC<{ record: ParentConfigValue }> = ({ record }) => {
  if (record.values && record.values.length > 0) {
    return (
      <>
        {record.values.map((value, index) => (
          <div
            key={index}
            className={value.is_anonymous ? 'default-section-text' : 'child-config-item'}
          >
            <ConfigurationKey record={value} />
            <ConfigurationValue record={value} />
          </div>
        ))}
      </>
    );
  }
  return <></>;
};
