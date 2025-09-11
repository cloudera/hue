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
import Button from 'cuix/dist/components/Button/Button';
import Loading from 'cuix/dist/components/Loading';
import DataSetsIcon from '@cloudera/cuix-core/icons/react/DataSetsIcon';
import PageHeader from './PageHeader';

import { i18nReact } from '../../../utils/i18nReact';
import type { Connector, Namespace, Compute } from '../../../config/types';
import Tabs, { type TabKey } from './Tabs';
import Toolbar from './Toolbar';
import Overview from './Overview';
import SampleGrid from './SampleGrid';
import DetailsProperties from './DetailsProperties';
import Partitions from './Partitions';
import ViewSql from './ViewSql';
import Queries from './Queries';
import Privileges from './Privileges';
import { notifyError } from '../utils/notifier';
import { getConnectorIdOrType } from '../utils/connector';
import { post } from '../../../api/utils';
import type { TableDetailsState } from '../utils/useTableDetails';

export interface TableDetailsProps {
  // Route and navigation
  sourceType?: string;
  database: string;
  table: string;
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  onBackToTables: () => void;

  // Data catalog context
  connector: Connector | null;
  namespace: Namespace | null;
  compute: Compute | null;

  // Table data
  tableDetails: TableDetailsState;

  // Actions
  onReloadTables: () => Promise<void>;

  // Breadcrumbs props
  sourceOptions?: string[];
  onSelectSource?: (sourceType: string) => void;
  onClickDataSources?: () => void;
  onClickDatabases?: () => void;
  onClickDatabase?: (database: string) => void;
}

const TableDetails = ({
  sourceType,
  database,
  table,
  activeTab,
  onTabChange,
  onBackToTables,
  connector,
  namespace,
  compute,
  tableDetails,
  onReloadTables,
  sourceOptions,
  onSelectSource,
  onClickDataSources,
  onClickDatabases,
  onClickDatabase
}: TableDetailsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const {
    loading: loadingData,
    overviewProps,
    detailsColumns,
    detailsProperties,
    detailsSections,
    sampleData,
    refresh
  } = tableDetails;

  const handleDropTable = async (skipTrash = false): Promise<void> => {
    // Optimistic UI update - immediately navigate back
    onBackToTables();

    try {
      // Create URLSearchParams for proper form encoding without qs array notation
      const formData = new URLSearchParams();
      formData.append('table_selection', table);
      formData.append('is_embeddable', 'true');
      formData.append('skip_trash', skipTrash ? 'on' : 'off');
      formData.append('source_type', sourceType || getConnectorIdOrType(connector) || 'hive');
      formData.append('start_time', Date.now().toString());

      if (namespace) {
        formData.append('namespace', JSON.stringify(namespace));
      }

      if (compute) {
        formData.append('cluster', JSON.stringify(compute));
      }

      const result = await post<{ history_uuid?: string; message?: string }>(
        `/metastore/tables/drop/${encodeURIComponent(database)}`,
        formData,
        {
          silenceErrors: false,
          qsEncodeData: false // Don't use qs.stringify, send URLSearchParams directly
        }
      );

      // Handle the task execution response
      if (result?.message) {
        notifyError(result.message);
        // If there's an error message, reload tables to restore state
        await onReloadTables();
        return;
      }

      // For successful operations (with or without history_uuid), reload tables
      await onReloadTables();
    } catch (error) {
      notifyError(t('Failed to drop table'));
      // On error, reload tables to restore the correct state
      await onReloadTables();
      throw error;
    }
  };

  return (
    <div>
      <PageHeader
        title={table}
        icon={<DataSetsIcon />}
        onRefresh={refresh}
        loading={loadingData}
        isRefreshing={false}
        sourceType={sourceType}
        database={database}
        table={table}
        sourceOptions={sourceOptions}
        onSelectSource={onSelectSource}
        onClickDataSources={onClickDataSources}
        onClickDatabases={onClickDatabases}
        onClickDatabase={onClickDatabase}
      />

      <div className="hue-table-browser__header-with-actions-only">
        <Toolbar
          sourceType={sourceType || getConnectorIdOrType(connector) || 'hive'}
          database={database}
          table={table}
          onRefresh={refresh}
          onDrop={handleDropTable}
          showQuery={true}
          showLoadData={true}
          showDrop={true}
          showRefresh={false}
        />
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={onTabChange}
        sampleCount={sampleData?.rows?.length}
        partitionsCount={overviewProps?.stats ? Number(overviewProps?.stats?.files) : undefined}
      />

      <Loading spinning={false}>
        {activeTab === 'overview' && (
          <Overview
            properties={overviewProps?.properties}
            stats={overviewProps?.stats}
            hdfsLink={overviewProps?.hdfsLink}
            columns={detailsColumns}
            loadingProperties={loadingData && !overviewProps?.properties}
            loadingStats={loadingData && !overviewProps?.stats}
            loadingColumns={loadingData && !detailsColumns.length}
            onRefreshStats={async () => {
              await refresh();
            }}
          />
        )}
        {activeTab === 'sample' && (
          <Loading spinning={loadingData && !sampleData}>
            <SampleGrid data={sampleData} />
          </Loading>
        )}
        {activeTab === 'details' && (
          <Loading
            spinning={
              loadingData &&
              !(
                detailsProperties?.length ||
                detailsSections.baseInfo?.length ||
                detailsSections.tableParameters?.length ||
                detailsSections.storageInfo?.length ||
                detailsSections.storageDescParams?.length
              )
            }
          >
            <DetailsProperties
              properties={detailsProperties}
              baseInfo={detailsSections.baseInfo}
              tableParameters={detailsSections.tableParameters}
              storageInfo={detailsSections.storageInfo}
              storageDescParams={detailsSections.storageDescParams}
            />
          </Loading>
        )}
        {activeTab === 'partitions' && (
          <Loading spinning={loadingData && !overviewProps}>
            <Partitions
              connector={connector}
              namespace={namespace}
              compute={compute}
              database={database}
              table={table}
              onCountChange={() => {}}
            />
          </Loading>
        )}
        {activeTab === 'queries' && (
          <Loading spinning={loadingData && !overviewProps}>
            <Queries
              connector={connector}
              namespace={namespace}
              compute={compute}
              database={database}
              table={table}
            />
          </Loading>
        )}
        {activeTab === 'viewSql' && (
          <Loading spinning={loadingData && !overviewProps?.properties}>
            <ViewSql
              sql={
                (overviewProps?.properties || []).find(
                  p =>
                    p.name.toLowerCase() === 'view original text:' ||
                    p.name.toLowerCase() === 'original query:'
                )?.value
              }
            />
          </Loading>
        )}
        {activeTab === 'privileges' && (
          <Loading spinning={loadingData && !overviewProps}>
            <Privileges database={database} table={table} />
          </Loading>
        )}
      </Loading>

      <div style={{ marginTop: 12 }}>
        <Button onClick={onBackToTables} data-testid="tb-back">
          {t('Back to tables')}
        </Button>
      </div>
    </div>
  );
};

export default TableDetails;
