// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import EmptyState from 'cuix/dist/components/EmptyState';
import { i18nReact } from '../../../utils/i18nReact';

export interface PrivilegesProps {
  database?: string;
  table?: string;
}

const Privileges = ({ database, table }: PrivilegesProps): JSX.Element => {
  // Placeholder: integrate KO sentry privileges via reactWrapper in a follow-up
  const { t } = i18nReact.useTranslation();
  if (!database || !table) {
    return <EmptyState title={t('No privileges')} />;
  }
  return <EmptyState title={t('Privileges for {{dbTable}}', { dbTable: `${database}.${table}` })} />;
};

export default Privileges;


