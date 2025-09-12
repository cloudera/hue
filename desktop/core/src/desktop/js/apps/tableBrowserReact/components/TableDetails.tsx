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

import React, { useState, useMemo } from 'react';
import Button from 'cuix/dist/components/Button/Button';
import Loading from 'cuix/dist/components/Loading';
import Modal from 'cuix/dist/components/Modal';
import DataSetsIcon from '@cloudera/cuix-core/icons/react/DataSetsIcon';
import ViewIcon from '@cloudera/cuix-core/icons/react/ViewIcon';
import PageHeader from './PageHeader';

import { i18nReact } from '../../../utils/i18nReact';
import huePubSub from '../../../utils/huePubSub';
import type { Connector, Namespace, Compute } from '../../../config/types';
import Tabs, { type TabKey } from './Tabs';
import Toolbar, { type ToolbarAction } from './Toolbar';
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
  const [isDropping, setIsDropping] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [skipTrash, setSkipTrash] = useState(false);
  const {
    loading: loadingData,
    isRefreshing,
    overviewProps,
    detailsColumns,
    detailsProperties,
    detailsSections,
    sampleData,
    refresh
  } = tableDetails;

  // Only show partitions tab if there are partitions
  const hasPartitions =
    overviewProps?.properties?.find(p => p.name === t('Partitioned'))?.value === t('Yes');

  // Determine if this is a view to show appropriate icon
  const isView = overviewProps?.properties?.find(p => p.name === t('Type'))?.value === t('View');

  const handleDropTable = async (skipTrash = false): Promise<void> => {
    // Prevent multiple simultaneous drop operations
    if (isDropping) {
      return;
    }

    setIsDropping(true);

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
      // Only navigate back after successful completion
      onBackToTables();
    } catch (error) {
      notifyError(t('Failed to drop table'));
      // On error, reload tables to restore the correct state
      await onReloadTables();
      throw error;
    } finally {
      setIsDropping(false);
    }
  };

  const openQuery = (): void => {
    const type = sourceType || 'hive';
    const query = database && table ? `SELECT * FROM ${database}.${table} LIMIT 100;` : '';
    huePubSub.publish('open.editor.new.prefilled.query', {
      type,
      query
    });
  };

  const toolbarActions = useMemo((): ToolbarAction[] => {
    const actions: ToolbarAction[] = [];

    // Query action
    actions.push({
      key: 'query',
      label: t('Query'),
      onClick: openQuery,
      variant: 'primary',
      disabled: !database || !table
    });

    // Load Data action
    actions.push({
      key: 'loadData',
      label: t('Load Data'),
      onClick: () => {
        // TODO: Implement load data functionality
      },
      disabled: !database || !table,
      tooltip: t('Load data into table')
    });

    // Drop action
    actions.push({
      key: 'drop',
      label: t('Drop'),
      onClick: () => setConfirmOpen(true),
      variant: 'danger',
      disabled: !database || !table || isDropping,
      tooltip: t('Drop table')
    });

    return actions;
  }, [t, database, table, isDropping]);

  return (
    <div>
      <PageHeader
        title={table}
        icon={isView ? <ViewIcon /> : <DataSetsIcon />}
        onRefresh={refresh}
        loading={loadingData}
        isRefreshing={isRefreshing}
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
        <Toolbar actions={toolbarActions} loading={isDropping} />
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={onTabChange}
        sampleCount={sampleData?.rows?.length}
        partitionsCount={overviewProps?.stats ? Number(overviewProps?.stats?.files) : undefined}
        showPartitions={!!hasPartitions}
      />

      <Loading spinning={false}>
        {activeTab === 'overview' && (
          <Overview
            properties={overviewProps?.properties}
            stats={overviewProps?.stats}
            hdfsLink={overviewProps?.hdfsLink}
            columns={detailsColumns}
            sampleData={sampleData}
            loadingProperties={(loadingData && !overviewProps?.properties) || isRefreshing}
            loadingStats={(loadingData && !overviewProps?.stats) || isRefreshing}
            loadingColumns={(loadingData && !detailsColumns.length) || isRefreshing}
            connector={connector}
            namespace={namespace}
            compute={compute}
            database={database}
            table={table}
            onRefreshStats={async () => {
              await refresh();
            }}
          />
        )}
        {activeTab === 'sample' && (
          <Loading spinning={(loadingData && !sampleData) || isRefreshing}>
            <SampleGrid data={sampleData} />
          </Loading>
        )}
        {activeTab === 'details' && (
          <Loading
            spinning={
              (loadingData &&
                !(
                  detailsProperties?.length ||
                  detailsSections.baseInfo?.length ||
                  detailsSections.tableParameters?.length ||
                  detailsSections.storageInfo?.length ||
                  detailsSections.storageDescParams?.length
                )) ||
              isRefreshing
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
        {activeTab === 'partitions' && hasPartitions && (
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

      <Modal
        open={confirmOpen}
        title={t('Drop table')}
        okText={t('Drop')}
        okButtonProps={{ danger: true }}
        cancelText={t('Cancel')}
        onCancel={() => {
          setConfirmOpen(false);
          setSkipTrash(false);
        }}
        onOk={async () => {
          try {
            await handleDropTable(skipTrash);
          } finally {
            setConfirmOpen(false);
            setSkipTrash(false);
          }
        }}
      >
        <div style={{ marginBottom: 16 }}>
          {t('Do you really want to drop table "{{tableName}}"?', { tableName: table })}
        </div>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="checkbox"
            checked={skipTrash}
            onChange={e => setSkipTrash(e.target.checked)}
          />
          {t('Skip the trash')}
        </label>
      </Modal>
    </div>
  );
};

export default TableDetails;
