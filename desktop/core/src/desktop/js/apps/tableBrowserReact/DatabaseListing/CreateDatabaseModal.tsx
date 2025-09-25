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

import React, { useMemo, useRef, useState, useCallback, memo } from 'react';
import { Checkbox, Input as AntdInput, Form } from 'antd';
import type { InputRef } from 'antd';
import { InfoCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import Input from 'cuix/dist/components/Input';
import Modal from 'cuix/dist/components/Modal';
import Tooltip from 'cuix/dist/components/Tooltip';
import { i18nReact } from '../../../utils/i18nReact';
import useDebouncedDatabaseValidation from '../hooks/useDebouncedDatabaseValidation';
import './CreateDatabaseModal.scss';

interface CreateDatabaseForm {
  name: string;
  comment: string;
  location: string;
  useDefaultLocation: boolean;
}

export interface CreateDatabaseModalProps {
  open: boolean;
  sourceType?: string;
  onCancel: () => void;
  onSubmit: (name: string, comment?: string, location?: string) => Promise<void>;
  getContainer?: () => HTMLElement;
}

// Memoized input component to prevent re-renders
// Note: Using Ant Design Input instead of CUIX Input because:
// - Need InputRef for focus management (nameInputRef.current.focus())
// - Form integration with antd.Form.Item requires antd form controls
// - Advanced props like 'suffix' and 'status' for validation states
const MemoizedDatabaseNameInput = memo(
  ({
    inputRef,
    placeholder,
    value,
    onChange,
    maxLength,
    status,
    suffix,
    autoFocus
  }: {
    inputRef: React.RefObject<InputRef>;
    placeholder: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    maxLength: number;
    status?: 'error' | undefined;
    suffix?: React.ReactNode;
    autoFocus?: boolean;
  }) => (
    <AntdInput
      key="database-name-input"
      className="hue-antd-input-cuix-styled"
      ref={inputRef}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      maxLength={maxLength}
      status={status}
      suffix={suffix}
      autoFocus={autoFocus} // eslint-disable-line jsx-a11y/no-autofocus
    />
  )
);

const CreateDatabaseModal: React.FC<CreateDatabaseModalProps> = ({
  open,
  sourceType,
  onCancel,
  onSubmit,
  getContainer
}) => {
  const { t } = i18nReact.useTranslation();
  const nameInputRef = useRef<InputRef>(null);

  const [form, setForm] = useState<CreateDatabaseForm>({
    name: '',
    comment: '',
    location: '',
    useDefaultLocation: true
  });

  // Validate database name with debounced uniqueness check
  const {
    validation: nameValidation,
    isValidating,
    hasValidated
  } = useDebouncedDatabaseValidation({
    name: form.name,
    dialect: sourceType || 'hive',
    debounceMs: 500
  });

  const isFormValid = useMemo(() => {
    return form.name.length > 0 && hasValidated && nameValidation.isValid && !isValidating;
  }, [form.name, hasValidated, nameValidation.isValid, isValidating]);

  // Memoize validation-related props to prevent input re-renders
  const inputStatus = useMemo(() => {
    return !nameValidation.isValid ? 'error' : undefined;
  }, [nameValidation.isValid]);

  // Create a stable suffix that's always present to prevent DOM structure changes
  const inputSuffix = useMemo(
    () => (
      <LoadingOutlined
        style={{
          color: '#1890ff',
          opacity: isValidating ? 1 : 0,
          visibility: isValidating ? 'visible' : 'hidden'
        }}
      />
    ),
    [isValidating]
  );

  const formItemValidateStatus = useMemo(() => {
    return !nameValidation.isValid ? 'error' : undefined;
  }, [nameValidation.isValid]);

  const formItemHelp = useMemo(() => {
    return !nameValidation.isValid ? nameValidation.error : '';
  }, [nameValidation.isValid, nameValidation.error]);

  const getDescriptionTooltip = useMemo(() => {
    const isHiveSource = sourceType === 'hive' || sourceType === 'impala';
    if (isHiveSource) {
      return t(
        'Descriptions are stored as database comments in the Hive metastore and are searchable.'
      );
    }
    return t('Descriptions are stored as database comments and are searchable.');
  }, [sourceType, t]);

  // Stable callback handlers to prevent re-renders
  const handleNameChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prevForm => ({ ...prevForm, name: e.target.value }));
  }, []);

  const handleCommentChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setForm(prevForm => ({ ...prevForm, comment: e.target.value }));
  }, []);

  const handleLocationChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prevForm => ({ ...prevForm, location: e.target.value }));
  }, []);

  const handleUseDefaultLocationChange = useCallback((e: { target: { checked: boolean } }) => {
    setForm(prevForm => ({ ...prevForm, useDefaultLocation: e.target.checked }));
  }, []);

  const resetForm = useCallback(() => {
    setForm({
      name: '',
      comment: '',
      location: '',
      useDefaultLocation: true
    });
  }, []);

  const handleCancel = useCallback(() => {
    resetForm();
    onCancel();
  }, [resetForm, onCancel]);

  const handleSubmit = useCallback(async () => {
    if (!isFormValid) {
      return;
    }

    try {
      await onSubmit(
        form.name.trim(),
        form.comment.trim() || undefined,
        form.useDefaultLocation ? undefined : form.location.trim() || undefined
      );
      resetForm();
    } catch (error) {
      // Error handling is done by the parent component
      throw error;
    }
  }, [
    isFormValid,
    form.name,
    form.comment,
    form.location,
    form.useDefaultLocation,
    onSubmit,
    resetForm
  ]);

  return (
    <Modal
      open={open}
      title={t('Create a new database')}
      okText={t('Create')}
      cancelText={t('Cancel')}
      getContainer={getContainer}
      onCancel={handleCancel}
      onOk={handleSubmit}
      okButtonProps={{
        disabled: !isFormValid
      }}
    >
      <Form layout="vertical">
        <Form.Item
          label={
            <>
              * {t('Database Name')}
              <Tooltip
                title={t(
                  'Database names must be be globally unique and start with a letter or number and contain only letters, numbers, and underscores.'
                )}
              >
                <InfoCircleOutlined style={{ marginLeft: 4, color: '#8c8c8c' }} />
              </Tooltip>
            </>
          }
          validateStatus={formItemValidateStatus}
          help={formItemHelp}
        >
          <MemoizedDatabaseNameInput
            inputRef={nameInputRef}
            placeholder={t('e.g. sales_data')}
            value={form.name}
            onChange={handleNameChange}
            maxLength={128}
            status={inputStatus}
            suffix={inputSuffix}
            autoFocus={open} // eslint-disable-line jsx-a11y/no-autofocus
          />
        </Form.Item>

        <Form.Item
          label={
            <>
              {t('Description')}
              <Tooltip title={getDescriptionTooltip}>
                <InfoCircleOutlined style={{ marginLeft: 4, color: '#8c8c8c' }} />
              </Tooltip>
            </>
          }
        >
          <AntdInput.TextArea
            placeholder={t('e.g. Customer transaction data for Q4 2025')}
            value={form.comment}
            onChange={handleCommentChange}
            rows={2}
            maxLength={1024}
          />
        </Form.Item>

        <Form.Item>
          <Checkbox checked={form.useDefaultLocation} onChange={handleUseDefaultLocationChange}>
            {t('Use default location')}
          </Checkbox>
        </Form.Item>

        {!form.useDefaultLocation && (
          <Form.Item
            label={t('Location')}
            help={t('Path to HDFS directory or file of database data.')}
          >
            <Input
              placeholder={t('e.g. /user/hive/warehouse/sales_data.db')}
              value={form.location}
              onChange={handleLocationChange}
              maxLength={2048}
            />
          </Form.Item>
        )}
      </Form>
    </Modal>
  );
};

export default CreateDatabaseModal;
