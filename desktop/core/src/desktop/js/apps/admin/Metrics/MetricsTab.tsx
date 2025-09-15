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

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import MetricsTable, { MetricsResponse, MetricsTableProps } from './MetricsTable';
import Loading from 'cuix/dist/components/Loading';
import Alert from 'cuix/dist/components/Alert';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { i18nReact } from '../../../utils/i18nReact';
import AdminHeader from '../AdminHeader';

import './Metrics.scss';

const Metrics: React.FC = (): JSX.Element => {
  const [filteredKeys, setFilteredKeys] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedMetric, setSelectedMetric] = useState<string>('All');
  const [filteredMetricsData, setFilteredMetricsData] = useState<MetricsTableProps[]>([]);

  const {
    data: metrics,
    loading,
    error
  } = useLoadData<MetricsResponse>('/desktop/metrics/', {
    params: { format: 'json' },
    onSuccess: response => {
      const keys = Object.keys(response.metric).filter(
        key =>
          !key.startsWith('auth') &&
          !key.startsWith('multiprocessing') &&
          !key.startsWith('python.gc')
      );
      setFilteredKeys(keys);
    }
  });

  const parseMetricsData = useCallback(
    (data: MetricsResponse) => {
      return filteredKeys.map(key => ({
        caption: key,
        dataSource: Object.keys(data.metric[key]).map(subKey => ({
          name: subKey,
          value: data.metric[key][subKey]
        }))
      }));
    },
    [filteredKeys]
  );

  const processedData = useMemo(() => {
    if (!metrics) {
      return [];
    }

    const parsedData = parseMetricsData(metrics);
    return parsedData
      .map(tableData => ({
        ...tableData,
        dataSource: tableData.dataSource.filter(data =>
          data.name.toLowerCase().includes(searchQuery.toLowerCase())
        )
      }))
      .filter(tableData => tableData.dataSource.length > 0);
  }, [metrics, parseMetricsData, searchQuery]);

  useEffect(() => {
    setFilteredMetricsData(processedData);
  }, [processedData]);

  const handleMetricChange = (value: string) => {
    setSelectedMetric(value);
  };

  const handleFilterInputChange = (filterValue: string) => {
    setSearchQuery(filterValue);
  };

  const { t } = i18nReact.useTranslation();

  return (
    <div className="cuix antd metrics-component">
      <Loading spinning={loading}>
        {!error && (
          <AdminHeader
            options={['All', ...filteredKeys]}
            selectedValue={selectedMetric}
            onSelectChange={handleMetricChange}
            filterValue={searchQuery}
            onFilterChange={handleFilterInputChange}
            placeholder={t('Filter metrics...')}
          />
        )}

        {error && (
          <Alert
            message={`Error: ${error}`}
            description="Error in displaying the Metrics!"
            type="error"
          />
        )}

        <div
          className="metrics-component__table-group"
          data-testid="metrics-component__table-group"
        >
          {!error &&
            filteredMetricsData
              .filter(tableData => selectedMetric === 'All' || selectedMetric === tableData.caption)
              .map(tableData => (
                <div key={tableData.caption}>
                  <MetricsTable caption={tableData.caption} dataSource={tableData.dataSource} />
                </div>
              ))}
        </div>
      </Loading>
    </div>
  );
};

export default Metrics;
