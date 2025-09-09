// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useEffect, useState } from 'react';
import { List, Tag } from 'antd';
import EmptyState from 'cuix/dist/components/EmptyState';
import { i18nReact } from '../../../utils/i18nReact';
import Loading from 'cuix/dist/components/Loading';
import dataCatalog from '../../../catalog/dataCatalog';
import type { Connector, Compute, Namespace } from '../../../config/types';
import type { Partitions as PartitionsType } from '../../../catalog/DataCatalogEntry';

export interface PartitionsProps {
  connector?: Connector | null;
  namespace?: Namespace | null;
  compute?: Compute | null;
  database?: string;
  table?: string;
}

const Partitions = ({
  connector,
  namespace,
  compute,
  database,
  table
}: PartitionsProps): JSX.Element => {
  const [loading, setLoading] = useState(false);
  const [partitions, setPartitions] = useState<PartitionsType | null>(null);

  useEffect(() => {
    const fetch = async () => {
      if (!connector || !namespace || !compute || !database || !table) {
        setPartitions(null);
        return;
      }
      setLoading(true);
      try {
        const entry = await dataCatalog.getEntry({
          connector,
          namespace,
          compute,
          path: [database, table]
        });
        const parts = await entry.getPartitions();
        setPartitions(parts);
      } catch (err) {
        setPartitions(null);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [connector, namespace, compute, database, table]);

  const { t } = i18nReact.useTranslation();

  if (
    !loading &&
    (!partitions ||
      !partitions.partition_values_json ||
      partitions.partition_values_json.length === 0)
  ) {
    return <EmptyState title={t('No partitions')} />;
  }

  return (
    <Loading spinning={loading}>
      <div style={{ marginBottom: 8 }}>
        {(partitions?.partition_keys_json || []).map((k, idx) => (
          <Tag key={idx}>{k}</Tag>
        ))}
      </div>
      <List
        bordered
        size="small"
        dataSource={partitions?.partition_values_json || []}
        renderItem={item => <List.Item>{item.partitionSpec}</List.Item>}
      />
    </Loading>
  );
};
export default Partitions;
