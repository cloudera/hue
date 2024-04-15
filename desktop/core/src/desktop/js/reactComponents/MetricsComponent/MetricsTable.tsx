// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, { CSSProperties } from 'react';
import Table from 'cuix/dist/components/Table/Table';
import type { ColumnType } from 'antd/es/table';
import './MetricsComponent.scss';
import 'cuix/dist/components/Table/Table.css';

interface MetricsTime {
  '1m_rate': number;
  '5m_rate': number;
  '15m_rate': number;
  '75_percentile': number;
  '95_percentile': number;
  '99_percentile': number;
  '999_percentile': number;
  'avg': number;
  'count': number;
  'max': number;
  'mean_rate': number;
  'min': number;
  'std_dev': number;
  'sum': number;
}

export interface MetricsResponse {
  metric: {
    'auth.ldap.auth-time': MetricsTime;
    'auth.oauth.auth-time': MetricsTime;
    'auth.pam.auth-time': MetricsTime;
    'auth.saml2.auth-time': MetricsTime;
    'auth.spnego.auth-time': MetricsTime;
    'multiprocessing.processes.daemon': MetricsValue;
    'multiprocessing.processes.total': MetricsValue;
    'python.gc.generation.0': MetricsValue;
    'python.gc.generation.1': MetricsValue;
    'python.gc.generation.2': MetricsValue;
    'python.gc.objects': MetricsValue;
    'queries.number': MetricsValue;
    'requests.active': MetricsCount;
    'requests.exceptions': MetricsCount;
    'requests.response-time': MetricsTime;
    'threads.daemon': MetricsValue;
    'threads.total': MetricsValue;
    'users': MetricsValue;
    'users.active': MetricsValue;
    'users.active.total': MetricsValue;
    'timestamp': string;
  };
}

interface MetricsValue {
  value: number;
}

interface MetricsCount {
  count: number;
}

interface MetricsTableProps {
  caption: string;
  dataSource: { name: string; value: any }[];
}

const MetricsTable = ({ caption, dataSource }: MetricsTableProps) => {
  const metricsColumns: ColumnType[] = [];

  metricsColumns.push({
    title: 'Name',
    dataIndex: 'name',
    key: 'name'
  });
  metricsColumns.push({
    title: 'Value',
    dataIndex: 'value',
    key: 'value'
  });

  return (
    <>
      <h4>{caption}</h4>
      <Table
        dataSource={dataSource}
        rowKey="name"
        columns={metricsColumns}
        style={CSSProperties}
        pagination={false}
      />
    </>
  );
};

export default MetricsTable;
