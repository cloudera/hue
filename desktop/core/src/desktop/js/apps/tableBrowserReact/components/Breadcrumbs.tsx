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

import React, { useMemo } from 'react';
import { i18nReact } from '../../../utils/i18nReact';
// import changeURL from '../../../utils/url/changeURL';

export interface BreadcrumbsProps {
  sourceType?: string;
  database?: string;
  table?: string;
  sourceOptions?: string[];
  onSelectSource?: (sourceType: string) => void;
  onClickDataSources?: () => void;
  onClickDatabases?: () => void;
  onClickDatabase?: (database: string) => void;
}

const Breadcrumbs = ({
  sourceType,
  database,
  table,
  // sourceOptions,
  // onSelectSource,
  onClickDataSources,
  onClickDatabases,
  onClickDatabase
}: BreadcrumbsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  // noop helper removed; directly calling changeURL

  const base = window.location.pathname.split('/tablebrowser')[0] || '';

  // no-op retained for compatibility

  const { sourcesHref, databasesHref, databaseHref } = useMemo(() => {
    const dh = `${base}/tablebrowser/${encodeURIComponent(sourceType || 'hive')}`;
    const dbh = `${dh}${database ? `/${encodeURIComponent(database)}` : ''}`;
    const sh = `${base}/tablebrowser/`;
    return { sourcesHref: sh, databasesHref: dh, databaseHref: dbh };
  }, [base, sourceType, database, table, t]);

  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
      <nav aria-label={t('Breadcrumbs')} style={{ flex: 1, minWidth: 0 }}>
        <ol
          style={{
            display: 'inline-flex',
            verticalAlign: 'middle',
            alignItems: 'center',
            gap: 8,
            whiteSpace: 'nowrap',
            margin: 0,
            padding: 0,
            listStyle: 'none',
            overflow: 'hidden'
          }}
        >
          <li>
            {!sourceType ? (
              <span aria-current="page">{t('Data sources')}</span>
            ) : (
              <a
                href={sourcesHref}
                aria-label={t('Data sources')}
                style={{ textDecoration: 'none' }}
                onClick={e => {
                  if (onClickDataSources) {
                    e.preventDefault();
                    onClickDataSources();
                  }
                }}
              >
                {t('Data sources')}
              </a>
            )}
          </li>
          {sourceType && (
            <>
              <li aria-hidden="true" role="presentation">
                /
              </li>
              <li>
                <a
                  href={databasesHref}
                  aria-label={(sourceType || 'hive').toUpperCase()}
                  style={{ textDecoration: 'none' }}
                  onClick={e => {
                    if (onClickDatabases) {
                      e.preventDefault();
                      onClickDatabases();
                    }
                  }}
                >
                  {(sourceType || 'hive').toUpperCase()}
                </a>
              </li>
            </>
          )}
          {database && (
            <>
              <li aria-hidden="true" role="presentation">
                /
              </li>
              {table ? (
                <li>
                  <a
                    href={databaseHref}
                    aria-label={database}
                    style={{ textDecoration: 'none' }}
                    onClick={e => {
                      if (onClickDatabase) {
                        e.preventDefault();
                        onClickDatabase(database);
                      }
                    }}
                  >
                    {database}
                  </a>
                </li>
              ) : (
                <li>
                  <span aria-current="page">{database}</span>
                </li>
              )}
            </>
          )}
          {database && table && (
            <>
              <li aria-hidden="true" role="presentation">
                /
              </li>
              <li>
                <span aria-current="page">{table}</span>
              </li>
            </>
          )}
        </ol>
      </nav>
    </div>
  );
};

export default Breadcrumbs;
