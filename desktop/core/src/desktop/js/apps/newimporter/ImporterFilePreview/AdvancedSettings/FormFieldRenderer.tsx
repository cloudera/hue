// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React from 'react';
import { Checkbox, Input, Form, Tooltip, Select, Radio } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { i18nReact } from '../../../../utils/i18nReact';
import { FieldConfig, VisibilityContext } from './advancedSettingsConfig';

interface FormFieldRendererProps {
  field: FieldConfig;
  context: VisibilityContext;
  value: any;
  onChange: (fieldId: string, value: any) => void;
}

const FormFieldRenderer: React.FC<FormFieldRendererProps> = ({
  field,
  context,
  value,
  onChange
}) => {
  const { t } = i18nReact.useTranslation();

  // Check if field should be hidden
  if (field.isHidden && field.isHidden(context)) {
    return null;
  }

  const renderField = () => {
    switch (field.type) {
      case 'checkbox':
        return (
          <Checkbox checked={value} onChange={e => onChange(field.id, e.target.checked)}>
            {t(field.label || '')}
            {field.tooltip && (
              <Tooltip title={t(field.tooltip)}>
                <InfoCircleOutlined style={{ marginLeft: 4 }} />
              </Tooltip>
            )}
          </Checkbox>
        );

      case 'input':
        return (
          <Input
            value={value || ''}
            onChange={e => onChange(field.id, e.target.value)}
            placeholder={field.placeholder ? t(field.placeholder) : undefined}
          />
        );

      case 'select':
        return (
          <Select
            value={value}
            onChange={selectedValue => onChange(field.id, selectedValue)}
            options={field.options?.map(option => ({
              value: option.value,
              label: t(option.label)
            }))}
            placeholder={field.placeholder ? t(field.placeholder) : undefined}
            style={{ width: '100%' }}
            getPopupContainer={triggerNode => triggerNode.parentElement}
            bordered
          />
        );

      case 'radio':
        return (
          <Radio.Group value={value} onChange={e => onChange(field.id, e.target.value)}>
            {field.options?.map(option => (
              <Radio key={option.value} value={option.value}>
                {t(option.label)}
              </Radio>
            ))}
          </Radio.Group>
        );

      default:
        return null;
    }
  };

  return (
    <Form.Item
      label={field.type === 'input' || field.type === 'select' ? t(field.label || '') : undefined}
    >
      {renderField()}
    </Form.Item>
  );
};

export default FormFieldRenderer;
