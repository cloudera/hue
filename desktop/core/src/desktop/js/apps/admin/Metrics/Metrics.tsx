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
import './Metrics.scss';

const { Option } = Select;

const Metrics: React.FC = (): JSX.Element => {
  const [metrics, setMetrics] = useState<MetricsResponse>();
  const [filteredKeys, setFilteredKeys] = useState<string[]>([]);
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
        const keys = Object.keys(response.metric).filter(
          key =>
            !key.startsWith('auth') &&
            !key.startsWith('multiprocessing') &&
            !key.startsWith('python.gc')
        );
        setFilteredKeys(keys);
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
    return filteredKeys.map(key => ({
      caption: key,
      dataSource: Object.keys(data.metric[key]).map(subKey => ({
        name: subKey,
        value: data.metric[key][subKey]
      }))
    }));
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
              className="metrics-filter"
              placeholder="Filter metrics..."
              value={searchQuery}
              onChange={handleFilterInputChange}
              prefix={<SearchOutlined />}
            />

            <Select
              className="metrics-select"
              //to make sure antd class gets applied
              getPopupContainer={triggerNode => triggerNode.parentElement}
              ref={dropdownRef}
              value={selectedMetric}
              onChange={handleMetricChange}
              data-testid="metric-select"
            >
              <Option value="">All</Option>
              {filteredKeys.map(key => (
                <Option key={key} value={key}>
                  {key}
                </Option>
              ))}
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

export default Metrics;
