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

import React, { useState, useEffect, useRef } from 'react';
import MetricsTable, { MetricsResponse } from './MetricsTable';
import { Spin, Input, Select, Alert } from 'antd';
import { get } from 'api/utils';
import { SearchOutlined } from '@ant-design/icons';
import './MetricsComponent.scss';

const { Option } = Select;

const MetricsComponent = () => {
  const [metrics, setMetrics] = useState<MetricsResponse>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedMetric, setSelectedMetric] = useState<string>('');
  const [showAllTables, setShowAllTables] = useState(true);
  const [filteredMetricsData, setFilteredMetricsData] = useState<MetricsData[]>([]);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await get<MetricsResponse>('/desktop/metrics/', { format: 'json' });
        setMetrics(response);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (!metrics) {
      return;
    }

    const filteredData = parseMetricsData(metrics).filter(tableData =>
      tableData.dataSource.some(data => data.name.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    setFilteredMetricsData(filteredData);
  }, [searchQuery, metrics]);

  const parseMetricsData = (data: MetricsResponse) => {
    const metricsData = [
      {
        caption: 'queries.number',
        dataSource: [{ name: 'value', value: data.metric['queries.number'].value }]
      },
      {
        caption: 'requests.active',
        dataSource: [{ name: 'count', value: data.metric['requests.active'].count }]
      },
      {
        caption: 'requests.exceptions',
        dataSource: [{ name: 'count', value: data.metric['requests.exceptions'].count }]
      },
      {
        caption: 'requests.response-time',
        dataSource: [
          { name: '15m_rate', value: data.metric['requests.response-time']['15m_rate'] },
          { name: '1m_rate', value: data.metric['requests.response-time']['1m_rate'] },
          { name: '5m_rate', value: data.metric['requests.response-time']['5m_rate'] },
          { name: '75_percentile', value: data.metric['requests.response-time']['75_percentile'] },
          { name: '95_percentile', value: data.metric['requests.response-time']['95_percentile'] },
          {
            name: '999_percentile',
            value: data.metric['requests.response-time']['999_percentile']
          },
          { name: '99_percentile', value: data.metric['requests.response-time']['99_percentile'] },
          { name: 'avg', value: data.metric['requests.response-time']['avg'] },
          { name: 'count', value: data.metric['requests.response-time']['count'] },
          { name: 'max', value: data.metric['requests.response-time']['max'] },
          { name: 'mean_rate', value: data.metric['requests.response-time']['mean_rate'] },
          { name: 'min', value: data.metric['requests.response-time']['min'] },
          { name: 'std_dev', value: data.metric['requests.response-time']['std_dev'] },
          { name: 'sum', value: data.metric['requests.response-time']['sum'] }
        ]
      },
      {
        caption: 'threads.daemon',
        dataSource: [{ name: 'value', value: data.metric['threads.daemon'].value }]
      },
      {
        caption: 'threads.total',
        dataSource: [{ name: 'value', value: data.metric['threads.total'].value }]
      },
      { caption: 'users', dataSource: [{ name: 'value', value: data.metric['users'].value }] },
      {
        caption: 'users.active',
        dataSource: [{ name: 'value', value: data.metric['users.active'].value }]
      },
      {
        caption: 'users.active.total',
        dataSource: [{ name: 'value', value: data.metric['users.active.total'].value }]
      }
    ];
    return metricsData;
  };

  const handleMetricChange = (value: string) => {
    setSelectedMetric(value);
    setShowAllTables(value === '');
  };

  const handleFilterInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  return (
    <div className="cuix antd metrics-component">
      <Spin spinning={loading}>
        {!error && (
          <>
            <Input
              placeholder="Filter metrics..."
              value={searchQuery}
              onChange={handleFilterInputChange}
              prefix={<SearchOutlined />}
            />
            <Select
              data-testid="metric-select"
              //to make sure antd class gets applied
              getPopupContainer={triggerNode => triggerNode.parentElement}
              ref={dropdownRef}
              // placeholder="Choose a metric"
              value={selectedMetric}
              onChange={handleMetricChange}
            >
              <Option value="">All</Option>
              <Option value="queries.number">Queries Number</Option>
              <Option value="requests.active">Active Requests</Option>
              <Option value="requests.exceptions">Exceptional Requests</Option>
              <Option value="requests.response-time">Requests Response-time</Option>
              <Option value="threads.daemon">Daemon Threads</Option>
              <Option value="threads.total">Total Threads</Option>
              <Option value="users">Users</Option>
              <Option value="users.active">Active Users</Option>
              <Option value="users.active.total">Total Active Users</Option>
            </Select>
          </>
        )}

        {error && (
          <Alert
            message={`Error: ${error}`}
            description="Error in displaying the Metrics!"
            type="error"
          />
        )}

        {!error &&
          filteredMetricsData.map((tableData, index) => (
            <div key={index}>
              {(showAllTables || selectedMetric === tableData.caption) && (
                <MetricsTable caption={tableData.caption} dataSource={tableData.dataSource} />
              )}
            </div>
          ))}
      </Spin>
    </div>
  );
};

export default MetricsComponent;
