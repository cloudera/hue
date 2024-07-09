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
import { Input } from 'antd';
import Select from 'cuix/dist/components/Select/Select';
import { SearchOutlined } from '@ant-design/icons';
import { i18nReact } from '../../utils/i18nReact';
import './AdminHeader.scss';

const { Option } = Select;

interface AdminHeaderProps {
  options: string[];
  selectedValue: string;
  onSelectChange: (value: string) => void;
  filterValue: string;
  onFilterChange: (value: string) => void;
  placeholder: string;
  configAddress?: string;
}

const AdminHeader: React.FC<AdminHeaderProps> = ({
  options,
  selectedValue,
  onSelectChange,
  filterValue,
  onFilterChange,
  placeholder,
  configAddress
}) => {
  const { t } = i18nReact.useTranslation();
  return (
    <div className="admin-header">
      <Select
        value={selectedValue}
        onChange={value => onSelectChange(value)}
        className="admin-header__select-dropdown"
        getPopupContainer={triggerNode => triggerNode.parentElement}
        data-testid="admin-header--select"
      >
        {options.map(option => (
          <Option key={option} value={option}>
            {option}
          </Option>
        ))}
      </Select>

      <Input
        className="admin-header__input-filter"
        placeholder={placeholder}
        prefix={<SearchOutlined />}
        value={filterValue}
        onChange={e => onFilterChange(e.target.value)}
      />

      {configAddress && (
        <span>
          {t('Configuration files location:')}
          <span className="config__file-location-value">{configAddress}</span>
        </span>
      )}
    </div>
  );
};

export default AdminHeader;
