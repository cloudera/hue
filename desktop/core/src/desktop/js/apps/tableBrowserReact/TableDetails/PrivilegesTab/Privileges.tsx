// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useEffect, useMemo, useState } from 'react';
import EmptyState from 'cuix/dist/components/EmptyState';
import { i18nReact } from '../../../../utils/i18nReact';
import { post } from '../../../../api/utils';
import './Privileges.scss';

export interface PrivilegesProps {
  database?: string;
  table?: string;
}

type WirePrivilege = {
  server: string;
  database: string;
  table: string;
  column: string;
  URI: string;
  action: string;
  timestamp: number;
  roleName: string;
  grantOption: boolean;
  scope: 'SERVER' | 'DATABASE' | 'TABLE' | 'COLUMN' | 'URI';
};

const Privileges = ({ database, table }: PrivilegesProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  if (!database || !table) {
    return (
      <EmptyState
        title={t('You don’t have access')}
        subtitle={t('Ask an administrator to grant the required permissions.')}
      />
    );
  }
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [privileges, setPrivileges] = useState<WirePrivilege[] | undefined>();

  const authorizableHierarchy = useMemo(
    () => ({ server: 'server1', db: database, table, column: null }),
    [database, table]
  );

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError(undefined);
      try {
        const data = await post<{ status: number; privileges: WirePrivilege[] }>(
          '/security/api/hive/list_sentry_privileges_by_authorizable',
          {
            groupName: '',
            roleSet: JSON.stringify({ all: true, roles: [] }),
            authorizableHierarchy: JSON.stringify(authorizableHierarchy)
          }
        );
        if (!cancelled) {
          setPrivileges(data.privileges || []);
        }
      } catch (e) {
        if (!cancelled) {
          setError(String(e));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [authorizableHierarchy]);

  if (loading && !privileges) {
    return <div className="tb-privileges__loading">{t('Loading privileges...')}</div>;
  }

  if (error) {
    return (
      <EmptyState title={t('Failed to load privileges')} subtitle={t('Error: {{msg}}', { msg: error })} />
    );
  }

  if (!privileges || privileges.length === 0) {
    return (
      <EmptyState
        title={t('No permissions found')}
        subtitle={t('You might not have access to view privileges for {{dbTable}}.', {
          dbTable: `${database}.${table}`
        })}
      />
    );
  }

  return (
    <div className="tb-privileges">
      <div className="tb-privileges__meta">
        <strong>{t('Object')}:</strong> {database}.{table}
      </div>
      <div className="tb-privileges__list" role="table" aria-label={t('Privileges list')}>
        <div className="tb-privileges__row tb-privileges__row--header" role="row">
          <div className="tb-privileges__cell" role="columnheader">{t('Role')}</div>
          <div className="tb-privileges__cell" role="columnheader">{t('Scope')}</div>
          <div className="tb-privileges__cell" role="columnheader">{t('Action')}</div>
          <div className="tb-privileges__cell" role="columnheader">{t('Grant')}</div>
          <div className="tb-privileges__cell" role="columnheader">{t('When')}</div>
        </div>
        {privileges.map((p, idx) => (
          <div className="tb-privileges__row" role="row" key={`${p.roleName}-${idx}`}>
            <div className="tb-privileges__cell" role="cell">{p.roleName}</div>
            <div className="tb-privileges__cell" role="cell">{p.scope}</div>
            <div className="tb-privileges__cell" role="cell">{p.action}</div>
            <div className="tb-privileges__cell" role="cell">{p.grantOption ? t('Yes') : t('No')}</div>
            <div className="tb-privileges__cell" role="cell">{new Date(p.timestamp * 1000).toLocaleString()}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Privileges;
