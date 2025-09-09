// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import EmptyState from 'cuix/dist/components/EmptyState';
import { i18nReact } from '../../../utils/i18nReact';

export interface ViewSqlProps {
  sql?: string;
}

const ViewSql = ({ sql }: ViewSqlProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  if (!sql) {
    return <EmptyState title={t('No view SQL')} />;
  }
  return (
    <pre style={{ background: '#f6f8fa', padding: 12, overflowX: 'auto' }}>
      {sql}
    </pre>
  );
};

export default ViewSql;


