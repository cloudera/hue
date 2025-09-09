// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { Card, Col, Descriptions, Row } from 'antd';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';
import RefreshIcon from '@cloudera/cuix-core/icons/react/RefreshIcon';
import { i18nReact } from '../../../utils/i18nReact';

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
}

const Overview = ({ properties, stats, hdfsLink, onRefreshStats }: OverviewProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const statsTitle = (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span>{t('Stats')}</span>
      {onRefreshStats && (
        <BorderlessButton
          onClick={onRefreshStats}
          title={t('Refresh stats')}
          icon={<RefreshIcon />}
        />
      )}
    </div>
  );
  return (
    <Row gutter={16}>
      <Col span={12}>
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
      </Col>
      <Col span={12}>
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
      </Col>
    </Row>
  );
};

export default Overview;


