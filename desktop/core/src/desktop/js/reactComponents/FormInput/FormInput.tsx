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
import { Form, Radio, Tooltip, Input as AntdInput } from 'antd';
import './FormInput.scss';

export enum FieldType {
  CHECKBOX = 'checkbox',
  INPUT = 'input',
  TEXTAREA = 'textarea',
  SELECT = 'select',
  RADIO = 'radio'
}

export interface FieldOption {
  value: string;
  label: string;
}

export interface FieldConfig {
  name: string;
  type: FieldType;
  label?: string;
  placeholder?: string;
  tooltip?: string;
  options?: FieldOption[];
  hidden?: boolean;
  style?: React.CSSProperties;
  nested?: boolean;
  parentField?: string;
  className?: string;
}

interface FormInputProps<T = string> {
  field: FieldConfig;
  defaultValue?: T;
  loading?: boolean;
  value?: T;
  onChange: (fieldId: string, value: T) => void;
  error?: boolean;
}

const FormInput = <T,>({
  field,
  defaultValue,
  loading,
  value,
  onChange,
  error
}: FormInputProps<T>): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  // Check if field should be hidden
  if (field.hidden) {
    return <></>;
  }

  const renderLabel = () => (
    <>
      {field.label && t(field.label)}
      {field.tooltip && (
        <Tooltip title={t(field.tooltip)}>
          <InfoCircleOutlined className="hue-form-input__tooltip-icon" />
        </Tooltip>
      )}
    </>
  );

  const renderField = () => {
    switch (field.type) {
      case FieldType.CHECKBOX:
        return (
          <div className="hue-form-input__checkbox">
            <Input
              type="checkbox"
              checked={value as boolean}
              onChange={e => onChange(field.name, e.target.checked as T)}
              defaultChecked={value === undefined ? (defaultValue as boolean) : undefined}
              className={field.className}
              status={error ? 'error' : undefined}
              id={field.name}
            />
            <label htmlFor={field.name}>{renderLabel()}</label>
          </div>
        );

      case FieldType.INPUT:
        return (
          <Input
            value={value as string}
            onChange={e => onChange(field.name, e.target.value as T)}
            placeholder={field.placeholder ? t(field.placeholder) : undefined}
            className={field.className}
            status={error ? 'error' : undefined}
            id={field.name}
          />
        );

      case FieldType.TEXTAREA:
        return (
          <AntdInput.TextArea
            value={value as string}
            onChange={e => onChange(field.name, e.target.value as T)}
            placeholder={field.placeholder ? t(field.placeholder) : undefined}
            className={field.className}
            status={error ? 'error' : undefined}
            id={field.name}
            rows={3}
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
            className={`hue-form-input__select ${field.className}`}
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
            className={field.className}
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
      className="hue-form-input"
      label={field.type === FieldType.CHECKBOX || !field.label ? undefined : renderLabel()}
      htmlFor={field.name}
    >
      {renderField()}
    </Form.Item>
  );
};

export default FormInput;
