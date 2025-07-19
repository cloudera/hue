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
import Input from 'cuix/dist/components/Input';
import Select from 'cuix/dist/components/Select';
import { InfoCircleOutlined } from '@ant-design/icons';
import { i18nReact } from '../../utils/i18nReact';
import { Form, Radio, Tooltip } from 'antd';

export enum FieldType {
  CHECKBOX = 'checkbox',
  INPUT = 'input',
  SELECT = 'select',
  RADIO = 'radio'
}

export interface FieldOption {
  value: string;
  label: string;
}

export interface FieldConfig<U = unknown> {
  name: string;
  type: FieldType;
  label?: string;
  placeholder?: string;
  tooltip?: string;
  options?: FieldOption[];
  isHidden?: (context?: U) => boolean;
  style?: React.CSSProperties;
  nested?: boolean;
  parentField?: string;
}

interface FormInputProps<T = string, U = unknown> {
  field: FieldConfig<U>;
  context?: U;
  defaultValue?: T;
  loading: boolean;
  value?: T;
  className?: string;
  onChange: (fieldId: string, value: T) => void;
  error?: boolean;
}

const FormInput = <T, U = unknown>({
  field,
  context,
  defaultValue,
  loading,
  value,
  onChange,
  className,
  error
}: FormInputProps<T, U>): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  // Check if field should be hidden
  if (field.isHidden && field.isHidden(context)) {
    return <></>;
  }

  const renderLabel = () => (
    <>
      {field.label && t(field.label)}
      {field.tooltip && (
        <Tooltip title={t(field.tooltip)}>
          <InfoCircleOutlined style={{ marginLeft: 4 }} />
        </Tooltip>
      )}
    </>
  );

  const renderField = () => {
    switch (field.type) {
      case FieldType.CHECKBOX:
        return (
          <>
            <Input
              type="checkbox"
              checked={value as boolean}
              onChange={e => onChange(field.name, e.target.checked as T)}
              defaultChecked={value === undefined ? (defaultValue as boolean) : undefined}
              className={className}
              status={error ? 'error' : undefined}
              id={field.name}
            />
            <label htmlFor={field.name} style={{ marginLeft: 8 }}>
              {renderLabel()}
            </label>
          </>
        );

      case FieldType.INPUT:
        return (
          <Input
            value={value as string}
            onChange={e => onChange(field.name, e.target.value as T)}
            placeholder={field.placeholder ? t(field.placeholder) : undefined}
            className={className}
            status={error ? 'error' : undefined}
            id={field.name}
          />
        );

      case FieldType.SELECT:
        return (
          <Select
            value={value as string}
            onChange={selectedValue => onChange(field.name, selectedValue as T)}
            options={field.options?.map(option => ({
              value: option.value,
              label: t(option.label)
            }))}
            placeholder={field.placeholder ? t(field.placeholder) : undefined}
            getPopupContainer={triggerNode => triggerNode.parentElement}
            bordered
            loading={loading}
            defaultValue={defaultValue as string}
            className={className}
            status={error ? 'error' : undefined}
            id={field.name}
          />
        );

      case FieldType.RADIO:
        return (
          <Radio.Group
            value={value as string}
            defaultValue={defaultValue as string}
            onChange={e => onChange(field.name, e.target.value as T)}
            className={className}
            id={field.name}
          >
            {field.options?.map(option => (
              <Radio key={option.value} value={option.value}>
                {t(option.label)}
              </Radio>
            ))}
          </Radio.Group>
        );

      default:
        return <></>;
    }
  };

  return (
    <Form.Item
      label={field.type === FieldType.CHECKBOX ? undefined : renderLabel()}
      htmlFor={field.name}
    >
      {renderField()}
    </Form.Item>
  );
};

export default FormInput;
