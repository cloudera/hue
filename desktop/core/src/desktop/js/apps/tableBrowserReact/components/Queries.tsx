// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useEffect, useState } from 'react';
import { List } from 'antd';
import EmptyState from 'cuix/dist/components/EmptyState';
import Loading from 'cuix/dist/components/Loading';
import { i18nReact } from '../../../utils/i18nReact';
import dataCatalog from '../../../catalog/dataCatalog';
import type { Connector, Compute, Namespace } from '../../../config/types';

export interface QueriesProps {
  connector?: Connector | null;
  namespace?: Namespace | null;
  compute?: Compute | null;
  database?: string;
  table?: string;
}

const Queries = ({ connector, namespace, compute, database, table }: QueriesProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [loading, setLoading] = useState(false);
  const [queries, setQueries] = useState<string[]>([]);

  useEffect(() => {
    const fetch = async () => {
      if (!connector || !namespace || !compute || !database || !table) {
        setQueries([]);
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
        // Use SQL Analyzer popularity as a proxy for queries; legacy API requires server route
        const analysis = await entry.getAnalysis({ silenceErrors: true });
        const popular = (analysis as any).top_joins || [];
        const qs = popular.map(
          (j: any) => `${j.leftTable}.${j.leftColumn} = ${j.rightTable}.${j.rightColumn}`
        );
        setQueries(qs);
      } catch (err) {
        setQueries([]);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [connector, namespace, compute, database, table]);

  if (!loading && (!queries || queries.length === 0)) {
    return <EmptyState title={t('No queries found for the current table.')} />;
  }

  return (
    <Loading spinning={loading}>
      <List
        bordered
        size="small"
        dataSource={queries}
        renderItem={q => <List.Item>{q}</List.Item>}
      />
    </Loading>
  );
};

export default Queries;
