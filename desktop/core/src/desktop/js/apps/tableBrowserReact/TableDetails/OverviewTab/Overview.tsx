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

import React from 'react';
import { Col, Row } from 'antd';
import Loading from 'cuix/dist/components/Loading';
import { i18nReact } from '../../../../utils/i18nReact';
import Schema from './Schema';
import MetaDataDisplay, { type MetaDataGroup } from '../../sharedComponents/MetaDataDisplay';
import type { Connector, Compute, Namespace } from '../../../../config/types';

import './Overview.scss';

export interface TableStats {
  files?: number | string;
  rows?: number | string;
  totalSize?: string;
  lastUpdated?: string;
  schemaLastModified?: string;
}

export interface OverviewProps {
  properties?: { name: string; value: string }[];
  stats?: TableStats;
  hdfsLink?: string;
  onRefreshStats?: () => void;
  columns?: {
    name: string;
    type: string;
    comment?: string;
    sample?: string;
    isPartitionKey?: boolean;
  }[];
  sampleData?: { headers: string[]; rows: (string | number | null)[][] };
  loadingProperties?: boolean;
  loadingStats?: boolean;
  loadingColumns?: boolean;
  loadingSamples?: boolean;
  onOpenColumn?: (column: string) => void;
  connector?: Connector | null;
  namespace?: Namespace | null;
  compute?: Compute | null;
  database?: string;
  table?: string;
}

const Overview = ({
  properties: rawProperties,
  stats,
  hdfsLink,
  columns,
  sampleData,
  loadingProperties,
  loadingStats,
  loadingColumns,
  loadingSamples,
  onOpenColumn,
  connector,
  namespace,
  compute,
  database,
  table
}: OverviewProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  // Ensure properties is always an array
  const properties = Array.isArray(rawProperties) ? rawProperties : [];

  // Helper function to check if a group has meaningful data
  const hasValidData = (groups: MetaDataGroup[]): boolean => {
    return groups.some(group =>
      group.items.some(item => {
        const value = typeof item.value === 'string' ? item.value : String(item.value);
        return value && value !== '-' && value !== 'null' && value !== 'undefined';
      })
    );
  };

  // Prepare properties data for MetaDataDisplay
  const propertiesGroups: MetaDataGroup[] = [
    {
      items: [
        ...(hdfsLink
          ? [
              {
                key: 'location',
                label: t('Stored in'),
                value: <a href={hdfsLink}>{t('location')}</a>
              }
            ]
          : []),
        ...properties
          .filter(p => !(hdfsLink && p.name === t('Location'))) // Filter out Location if hdfsLink exists
          .map(p => ({
            key: p.name,
            label: p.name,
            value: p.value
          }))
      ]
    }
  ];

  // Prepare stats data for MetaDataDisplay
  const statsGroups: MetaDataGroup[] = [
    {
      items: [
        {
          key: 'files',
          label: t('Files'),
          value: stats?.files ?? '-'
        },
        {
          key: 'rows',
          label: t('Rows'),
          value: stats?.rows ?? '-'
        },
        {
          key: 'totalSize',
          label: t('Total size'),
          value: stats?.totalSize ?? '-'
        },
        {
          key: 'lastUpdated',
          label: t('Data last updated on'),
          value: stats?.lastUpdated ?? '-'
        },
        ...(stats?.schemaLastModified
          ? [
              {
                key: 'schemaLastModified',
                label: t('Schema last modified on'),
                value: stats.schemaLastModified
              }
            ]
          : [])
      ]
    }
  ];

  const showProperties = loadingProperties || hasValidData(propertiesGroups);
  const showStats = loadingStats || hasValidData(statsGroups);

  return (
    <div className="hue-table-details-overview">
      {(showProperties || showStats) && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          {showProperties && (
            <Col span={showStats ? 12 : 24}>
              <Loading spinning={!!loadingProperties}>
                <MetaDataDisplay groups={propertiesGroups} />
              </Loading>
            </Col>
          )}
          {showStats && (
            <Col span={showProperties ? 12 : 24}>
              <Loading spinning={!!loadingStats}>
                <MetaDataDisplay groups={statsGroups} />
              </Loading>
            </Col>
          )}
        </Row>
      )}

      <Loading spinning={!!loadingColumns}>
        {!!columns?.length && (
          <>
            <div className="hue-table-browser__header-with-actions">
              <h3 className="hue-h3">
                {t('{{label}} ({{count}})', {
                  label: t('Schema'),
                  count: columns.length
                })}
              </h3>
            </div>
            <Schema
              columns={columns}
              sampleData={sampleData}
              loadingSamples={loadingSamples}
              onOpenColumn={onOpenColumn}
              connector={connector}
              namespace={namespace}
              compute={compute}
              database={database}
              table={table}
            />
          </>
        )}
      </Loading>
    </div>
  );
};

export default Overview;
