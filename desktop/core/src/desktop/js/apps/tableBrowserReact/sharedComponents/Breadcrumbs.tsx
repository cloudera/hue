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

import './Breadcrumbs.scss';

export interface BreadcrumbsProps {
  sourceType?: string;
  database?: string;
  table?: string;
  column?: string;
  fields?: string[];
  sourceOptions?: string[];
  onSelectSource?: (sourceType: string) => void;
  onClickDataSources?: () => void;
  onClickDatabases?: () => void;
  onClickDatabase?: (database: string) => void;
  onClickTable?: (table: string) => void;
  onClickColumn?: () => void;
  onClickField?: (path: string[]) => void;
}

const Breadcrumbs = ({
  sourceType,
  database,
  table,
  column,
  fields = [],
  // sourceOptions,
  // onSelectSource,
  onClickDataSources,
  onClickDatabases,
  onClickDatabase,
  onClickTable,
  onClickColumn,
  onClickField
}: BreadcrumbsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  // noop helper removed; directly calling changeURL

  const base = window.location.pathname.split('/tablebrowser')[0] || '';

  // no-op retained for compatibility

  const { sourcesHref, databasesHref, databaseHref, tableHref } = useMemo(() => {
    const dh = `${base}/tablebrowser/${encodeURIComponent(sourceType || 'hive')}`;
    const dbh = `${dh}${database ? `/${encodeURIComponent(database)}` : ''}`;
    const th = `${dbh}${table ? `/${encodeURIComponent(table)}` : ''}`;
    const sh = `${base}/tablebrowser`;
    return { sourcesHref: sh, databasesHref: dh, databaseHref: dbh, tableHref: th };
  }, [base, sourceType, database, table, t]);

  return (
    <div
      className="hue-table-browser-breadcrumbs"
      style={{ display: 'flex', gap: 8, alignItems: 'center' }}
    >
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
              {column ? (
                <li>
                  <a
                    href={tableHref}
                    aria-label={table}
                    style={{ textDecoration: 'none' }}
                    onClick={e => {
                      if (onClickTable) {
                        e.preventDefault();
                        onClickTable(table);
                      }
                    }}
                  >
                    {table}
                  </a>
                </li>
              ) : (
                <li>
                  <span aria-current="page">{table}</span>
                </li>
              )}
            </>
          )}
          {database && table && column && (
            <>
              <li aria-hidden="true" role="presentation">
                /
              </li>
              <li>
                {fields && fields.length && onClickColumn ? (
                  <a
                    href={`${tableHref}/${encodeURIComponent(column)}`}
                    aria-label={column}
                    style={{ textDecoration: 'none' }}
                    onClick={e => {
                      e.preventDefault();
                      onClickColumn();
                    }}
                  >
                    {column}
                  </a>
                ) : (
                  <span aria-current="page">{column}</span>
                )}
              </li>
            </>
          )}
          {database &&
            table &&
            column &&
            fields &&
            fields.length > 0 &&
            fields.map((f, idx) => (
              <React.Fragment key={`${f}-${idx}`}>
                <li aria-hidden="true" role="presentation">
                  /
                </li>
                <li>
                  {idx < fields.length - 1 && onClickField ? (
                    <a
                      href={`${tableHref}/${encodeURIComponent(column!)}/${fields
                        .slice(0, idx + 1)
                        .map(encodeURIComponent)
                        .join('/')}`}
                      aria-label={f}
                      style={{ textDecoration: 'none' }}
                      onClick={e => {
                        e.preventDefault();
                        onClickField(fields.slice(0, idx + 1));
                      }}
                    >
                      {f}
                    </a>
                  ) : (
                    <span aria-current="page">{f}</span>
                  )}
                </li>
              </React.Fragment>
            ))}
        </ol>
      </nav>
    </div>
  );
};

export default Breadcrumbs;
