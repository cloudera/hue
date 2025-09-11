// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { Card, Col, Descriptions, Row } from 'antd';
import Loading from 'cuix/dist/components/Loading';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';
import RefreshIcon from '@cloudera/cuix-core/icons/react/RefreshIcon';
import { i18nReact } from '../../../utils/i18nReact';
import DetailsSchema from './DetailsSchema';

export interface TableStats {
  files?: number | string;
  rows?: number | string;
  totalSize?: string;
  lastUpdated?: string;
}

export interface OverviewProps {
  properties?: { name: string; value: string }[];
  stats?: TableStats;
  hdfsLink?: string;
  onRefreshStats?: () => void;
  columns?: { name: string; type: string; comment?: string; sample?: string }[];
  loadingProperties?: boolean;
  loadingStats?: boolean;
  loadingColumns?: boolean;
}

const Overview = ({
  properties,
  stats,
  hdfsLink,
  onRefreshStats,
  columns,
  loadingProperties,
  loadingStats,
  loadingColumns
}: OverviewProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const statsTitle = (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span>{t('Stats')}</span>
      {onRefreshStats && (
        <BorderlessButton
          aria-label={t('Refresh stats')}
          onClick={onRefreshStats}
          title={t('Refresh stats')}
          icon={<RefreshIcon />}
        />
      )}
    </div>
  );
  return (
    <div>
      <Row gutter={16}>
        <Col span={12}>
          <Loading spinning={!!loadingProperties}>
            <Card title={t('Properties')}>
              <Descriptions column={1} size="small" bordered>
                {hdfsLink && (
                  <Descriptions.Item label={t('Location')}>
                    <a href={hdfsLink}>{t('location')}</a>
                  </Descriptions.Item>
                )}
                {(properties || []).map(p => (
                  <Descriptions.Item key={p.name} label={p.name}>
                    {p.value}
                  </Descriptions.Item>
                ))}
              </Descriptions>
            </Card>
          </Loading>
        </Col>
        <Col span={12}>
          <Loading spinning={!!loadingStats}>
            <Card title={statsTitle}>
              <Descriptions column={1} size="small" bordered>
                <Descriptions.Item label={t('Files')}>{stats?.files ?? '-'}</Descriptions.Item>
                <Descriptions.Item label={t('Rows')}>{stats?.rows ?? '-'}</Descriptions.Item>
                <Descriptions.Item label={t('Total size')}>
                  {stats?.totalSize ?? '-'}
                </Descriptions.Item>
                <Descriptions.Item label={t('Last updated')}>
                  {stats?.lastUpdated ?? '-'}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Loading>
        </Col>
      </Row>
      <div style={{ marginTop: 16 }}>
        <Loading spinning={!!loadingColumns}>
          {!!columns?.length && (
            <Card title={t('Schema')}>
              <DetailsSchema columns={columns} />
            </Card>
          )}
        </Loading>
      </div>
    </div>
  );
};

export default Overview;
