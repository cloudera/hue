// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useMemo, useState } from 'react';
import { Input, Table } from 'antd';
import { i18nReact } from '../../../utils/i18nReact';

export interface ColumnDef {
  name: string;
  type: string;
  comment?: string;
  sample?: string;
}

export interface DetailsSchemaProps {
  columns: ColumnDef[];
}

const DetailsSchema = ({ columns }: DetailsSchemaProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [filter, setFilter] = useState('');

  const filtered = useMemo(() => {
    if (!filter) return columns;
    const q = filter.toLowerCase();
    return columns.filter(c => c.name.toLowerCase().includes(q) || (c.comment || '').toLowerCase().includes(q));
  }, [columns, filter]);

  return (
    <div>
      <Input.Search allowClear placeholder={t('Filter...')} style={{ marginBottom: 8 }} value={filter} onChange={e => setFilter(e.target.value)} />
      <Table
        size="small"
        pagination={false}
        columns={[
          { title: t('Column'), dataIndex: 'name' },
          { title: t('Type'), dataIndex: 'type' },
          { title: t('Description'), dataIndex: 'comment' },
          { title: t('Sample'), dataIndex: 'sample' }
        ]}
        dataSource={filtered.map((c, idx) => ({ key: idx, ...c }))}
      />
    </div>
  );
};

export default DetailsSchema;


