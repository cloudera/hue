// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import React from 'react';

import './MetaDataDisplay.scss';

export interface MetaDataItem {
  label: string;
  value: React.ReactNode;
  key?: string;
}

export interface MetaDataGroup {
  items: MetaDataItem[];
}

export interface MetaDataDisplayProps {
  groups: MetaDataGroup[];
  className?: string;
}

const MetaDataDisplay = ({ groups, className }: MetaDataDisplayProps): JSX.Element => {
  return (
    <div className={`meta-data ${className || ''}`}>
      {groups.map((group, groupIndex) => (
        <div key={`group-${groupIndex}`} className="meta-data__group">
          {group.items.map((item, itemIndex) => (
            <div key={item.key || `item-${itemIndex}`} className="meta-data__column">
              <div className="meta-data__column-label">{item.label}</div>
              <div className="meta-data__column-value">{item.value}</div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default MetaDataDisplay;
