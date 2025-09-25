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
import { Tooltip } from 'antd';
import { i18nReact } from '../../../utils/i18nReact';
// import changeURL from '../../../utils/url/changeURL';

import './Breadcrumbs.scss';
import { useNavigation } from './NavigationContext';
import { buildTableBrowserPath, getTableBrowserBasePath } from '../utils/routing';
import { truncateMiddle } from '../utils/textUtils';

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
  const nav = useNavigation();

  // noop helper removed; directly calling changeURL

  const base = getTableBrowserBasePath();

  // no-op retained for compatibility

  const { sourcesHref, databasesHref, databaseHref, tableHref } = useMemo(() => {
    const src = sourceType || 'hive';
    return {
      sourcesHref: buildTableBrowserPath(base),
      databasesHref: buildTableBrowserPath(base, src),
      databaseHref: buildTableBrowserPath(base, src, database),
      tableHref: buildTableBrowserPath(base, src, database, table)
    };
  }, [base, sourceType, database, table]);

  return (
    <div className="hue-table-browser-breadcrumbs">
      <nav aria-label={t('Breadcrumbs')}>
        <ol>
          <li>
            {!sourceType ? (
              <span aria-current="page">{t('Data sources')}</span>
            ) : (
              <a
                href={sourcesHref}
                aria-label={t('Data sources')}
                onClick={e => {
                  e.preventDefault();
                  (onClickDataSources || nav.navigateToSources)();
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
                  onClick={e => {
                    e.preventDefault();
                    (onClickDatabases || (() => nav.navigateToSource(sourceType || 'hive')))();
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
                  {(() => {
                    const { truncated, isTruncated } = truncateMiddle(database);
                    const linkElement = (
                      <a
                        href={databaseHref}
                        aria-label={database}
                        onClick={e => {
                          e.preventDefault();
                          (onClickDatabase || ((db: string) => nav.navigateToDatabase(db)))(
                            database
                          );
                        }}
                        className={isTruncated ? 'hue-breadcrumb-truncated' : ''}
                      >
                        {truncated}
                      </a>
                    );

                    return isTruncated ? (
                      <Tooltip title={database} placement="bottom">
                        {linkElement}
                      </Tooltip>
                    ) : (
                      linkElement
                    );
                  })()}
                </li>
              ) : (
                <li>
                  {(() => {
                    const { truncated, isTruncated } = truncateMiddle(database);
                    const spanElement = (
                      <span
                        aria-current="page"
                        className={isTruncated ? 'hue-breadcrumb-truncated' : ''}
                      >
                        {truncated}
                      </span>
                    );

                    return isTruncated ? (
                      <Tooltip title={database} placement="bottom">
                        {spanElement}
                      </Tooltip>
                    ) : (
                      spanElement
                    );
                  })()}
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
                  {(() => {
                    const { truncated, isTruncated } = truncateMiddle(table);
                    const linkElement = (
                      <a
                        href={tableHref}
                        aria-label={table}
                        onClick={e => {
                          e.preventDefault();
                          (onClickTable || ((tbl: string) => nav.navigateToTable(database!, tbl)))(
                            table
                          );
                        }}
                        className={isTruncated ? 'hue-breadcrumb-truncated' : ''}
                      >
                        {truncated}
                      </a>
                    );

                    return isTruncated ? (
                      <Tooltip title={table} placement="bottom">
                        {linkElement}
                      </Tooltip>
                    ) : (
                      linkElement
                    );
                  })()}
                </li>
              ) : (
                <li>
                  {(() => {
                    const { truncated, isTruncated } = truncateMiddle(table);
                    const spanElement = (
                      <span
                        aria-current="page"
                        className={isTruncated ? 'hue-breadcrumb-truncated' : ''}
                      >
                        {truncated}
                      </span>
                    );

                    return isTruncated ? (
                      <Tooltip title={table} placement="bottom">
                        {spanElement}
                      </Tooltip>
                    ) : (
                      spanElement
                    );
                  })()}
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
                    onClick={e => {
                      e.preventDefault();
                      (onClickColumn || (() => nav.navigateToColumn(database!, table!, column!)))();
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
                  {idx < fields.length - 1 ? (
                    <a
                      href={`${tableHref}/${encodeURIComponent(column!)}/${fields
                        .slice(0, idx + 1)
                        .map(encodeURIComponent)
                        .join('/')}`}
                      aria-label={f}
                      onClick={e => {
                        e.preventDefault();
                        const handler =
                          onClickField ||
                          ((path: string[]) =>
                            nav.navigateToField(database!, table!, column!, path));
                        handler(fields.slice(0, idx + 1));
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
