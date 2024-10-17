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
import { Select, Input } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import './AdminHeader.scss';

const { Option } = Select;

interface FilterSelectProps {
  options: string[];
  selectedValue: string;
  onSelectChange: (value: string) => void;
  filterValue: string;
  onFilterChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder: string;
  configAddress?: string;
}

const FilterSelect: React.FC<FilterSelectProps> = ({
  options,
  selectedValue,
  onSelectChange,
  filterValue,
  onFilterChange,
  placeholder,
  configAddress,
}) => {
  return (
    <div className='cuix antd admin-header-actions'>
      <Select
        value={selectedValue}
        onChange={onSelectChange}
        className="select-dropDown"
        getPopupContainer={triggerNode => triggerNode.parentElement}
      >
        {options.map(option => (
          <Option key={option} value={option}>
            {option}
          </Option>
        ))}
      </Select>

      <Input
        className="input-filter"
        placeholder={placeholder}
        prefix={<SearchOutlined />}
        value={filterValue}
        onChange={onFilterChange}
      />

      {configAddress && (
        <span>
          Configuration files location:<span className='config-file-address-value'>{configAddress}</span>
        </span>
      )}

    </div>
  );
};

export default FilterSelect;
