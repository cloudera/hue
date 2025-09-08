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

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Button, Col, Empty, List, Row, Spin } from 'antd';

import DataBrowserIcon from '@cloudera/cuix-core/icons/react/DataBrowserIcon';

import { i18nReact } from '../../utils/i18nReact';
import CommonHeader from '../../reactComponents/CommonHeader/CommonHeader';
import './TableBrowserPage.scss';
import changeURL from '../../utils/url/changeURL';
import { useDataCatalog } from '../../utils/hooks/useDataCatalog/useDataCatalog';

function parsePath(pathname: string): { sourceType?: string; database?: string; table?: string } {
  // Expect: <base>/tablebrowser[/<sourceType>[/<database>[/<table>]]]
  const idx = pathname.indexOf('/tablebrowser');
  if (idx === -1) {
    return {};
  }
  const rest = pathname.substring(idx + '/tablebrowser'.length);
  const segments = rest.split('/').filter(Boolean);
  return {
    sourceType: segments[0],
    database: segments[1],
    table: segments[2]
  };
}

const TableBrowserPage = (): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const route = useMemo(() => parsePath(window.location.pathname), [window.location.pathname]);

  const {
    loading: loadingStates,
    databases,
    database: currentDb,
    setDatabase: selectDb,
    tables
  } = useDataCatalog();

  const [table, setTable] = useState<string | undefined>(route.table);

  const updatePath = useCallback(
    (nextDatabase?: string, nextTable?: string) => {
      const urlPathname = window.location.pathname;
      const baseIdx = urlPathname.indexOf('/tablebrowser');
      const base = baseIdx !== -1 ? urlPathname.substring(0, baseIdx) : '';
      const sourceType = route.sourceType || 'hive';
      const nextPath = [
        base,
        '/tablebrowser',
        `/${encodeURIComponent(sourceType)}`,
        nextDatabase ? `/${encodeURIComponent(nextDatabase)}` : '',
        nextTable ? `/${encodeURIComponent(nextTable)}` : ''
      ].join('');
      changeURL(nextPath);
    },
    [window.location.pathname, route.sourceType]
  );

  // Initialize from URL on mount (partial sync)
  useEffect(() => {
    if (route.database) {
      selectDb(route.database);
    }
    if (route.table) {
      setTable(route.table);
    }
  }, []);

  const onPickMockDb = () => {
    const nextDb = databases?.[0] || 'default';
    selectDb(nextDb);
    setTable(undefined);
    updatePath(nextDb, undefined);
  };

  // Removed unused onPickMockTable (tables now come from the catalog)

  return (
    <div className="hue-table-browser cuix antd">
      <CommonHeader title={t('Table Browser')} icon={<DataBrowserIcon />} />
      <div className="hue-table-browser__container">
        <Row gutter={16}>
          <Col span={8}>
            <div className="hue-table-browser__panel" data-testid="tb-left-panel">
              {!currentDb && (
                <div>
                  <Empty description={t('No database selected.')} />
                  <Button type="primary" onClick={onPickMockDb} data-testid="tb-pick-db">
                    {t('Select default')}
                  </Button>
                </div>
              )}

              {!!currentDb && (
                <div>
                  <div style={{ marginBottom: 8 }}>{t('Databases')}</div>
                  <Spin spinning={!!loadingStates.database}>
                    <List
                      bordered
                      size="small"
                      dataSource={databases}
                      renderItem={item => (
                        <List.Item
                          className={item === currentDb ? 'ant-list-item-selected' : ''}
                          onClick={() => {
                            selectDb(item);
                            setTable(undefined);
                            updatePath(item, undefined);
                          }}
                          style={{ cursor: 'pointer' }}
                        >
                          <span>{item}</span>
                          {item === currentDb && (
                            <strong style={{ marginLeft: 8 }}>({t('selected')})</strong>
                          )}
                        </List.Item>
                      )}
                    />
                  </Spin>
                </div>
              )}
            </div>
          </Col>
          <Col span={16}>
            <div className="hue-table-browser__panel" data-testid="tb-right-panel">
              {!currentDb && <Empty description={t('Pick a database to get started')} />}

              {!!currentDb && !table && (
                <div>
                  <div style={{ marginBottom: 8 }}>{t('Tables')}</div>
                  <Spin spinning={!!loadingStates.table}>
                    <List
                      bordered
                      size="small"
                      dataSource={tables}
                      renderItem={item => (
                        <List.Item
                          onClick={() => {
                            setTable(item.name);
                            updatePath(currentDb, item.name);
                          }}
                          style={{ cursor: 'pointer' }}
                        >
                          <span>{item.name}</span>
                        </List.Item>
                      )}
                    />
                  </Spin>
                </div>
              )}

              {!!currentDb && !!table && (
                <div>
                  <h3 style={{ marginTop: 0 }}>
                    {t('Details for')} {currentDb}.{table}
                  </h3>
                  <p>{t('This is a placeholder for Columns, Partitions, Samples, Queries...')}</p>
                  <div style={{ marginTop: 12 }}>
                    <Button
                      onClick={() => {
                        setTable(undefined);
                        updatePath(currentDb, undefined);
                      }}
                      data-testid="tb-back"
                    >
                      {t('Back to tables')}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default TableBrowserPage;
