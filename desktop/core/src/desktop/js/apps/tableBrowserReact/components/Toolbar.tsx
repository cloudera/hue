// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information.
// Apache License 2.0 applies.

import React from 'react';
import { Button, Modal, Space, Tooltip } from 'antd';
import { i18nReact } from '../../../utils/i18nReact';
import huePubSub from '../../../utils/huePubSub';

export interface ToolbarProps {
  sourceType?: string;
  database?: string;
  table?: string;
  onRefresh?: () => void;
  onDrop?: () => Promise<void> | void;
  onLoadData?: () => Promise<void> | void;
}

const Toolbar = ({ sourceType, database, table, onRefresh, onDrop, onLoadData }: ToolbarProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const openQuery = (): void => {
    huePubSub.publish('open.editor.new.query', {
      type: sourceType || 'hive',
      statementType: 'text',
      statementPath: database && table ? `${database}.${table}` : undefined
    });
  };

  const dropTable = (): void => {
    if (!database || !table) return;
    Modal.confirm({
      title: t('Drop table'),
      content: `${database}.${table}`,
      okText: t('Drop'),
      okButtonProps: { danger: true },
      cancelText: t('Cancel'),
      onOk: async () => {
        try {
          if (onDrop) {
            await onDrop();
          }
          if (onRefresh) {
            onRefresh();
          }
        } catch (e) {
          if (onRefresh) {
            onRefresh();
          }
        }
      }
    });
  };

  return (
    <Space>
      <Button onClick={openQuery}>{t('Query')}</Button>
      <Tooltip title={t('Load data into table')}>
        <Button onClick={() => onLoadData?.()} disabled={!database || !table}>
          {t('Load Data')}
        </Button>
      </Tooltip>
      <Tooltip title={t('Drop table')}>
        <Button danger onClick={dropTable} disabled={!database || !table}>
          {t('Drop')}
        </Button>
      </Tooltip>
      <Button onClick={onRefresh}>{t('Refresh')}</Button>
    </Space>
  );
};

export default Toolbar;


