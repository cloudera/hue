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

import { useCallback, useEffect, useState } from 'react';
import { i18nReact } from '../../../utils/i18nReact';
import dataCatalog from '../../../catalog/dataCatalog';
import huePubSub from '../../../utils/huePubSub';
import { GLOBAL_ERROR_TOPIC } from '../../../reactComponents/GlobalAlert/events';
import formatBytes from '../../../utils/formatBytes';
import { formatTimestamp } from '../../../utils/dateTimeUtils';
import { post } from '../../../api/utils';
import { getConnectorIdOrType } from './connector';
import { getLastKnownConfig } from '../../../config/hueConfig';
import type { Analysis, SampleMeta } from '../../../catalog/DataCatalogEntry';
import type { Connector, Compute, Namespace } from '../../../config/types';
import type { TableStats } from '../components/Overview';

export interface UseTableDetailsArgs {
  connector?: Connector | null;
  namespace?: Namespace | null;
  compute?: Compute | null;
  database?: string;
  table?: string;
}

export interface TableDetailsState {
  loading: boolean;
  isRefreshing: boolean;
  overviewProps?: {
    properties?: { name: string; value: string }[];
    stats?: {
      files?: number | string;
      rows?: number | string;
      totalSize?: string;
      lastUpdated?: string;
      schemaLastModified?: string;
    };
    hdfsLink?: string;
  };
  detailsColumns: {
    name: string;
    type: string;
    comment?: string;
    sample?: string;
    isPartitionKey?: boolean;
  }[];
  detailsProperties: { name: string; value: string }[];
  detailsSections: {
    baseInfo?: { name: string; value: string }[];
    tableParameters?: { name: string; value: string }[];
    storageInfo?: { name: string; value: string }[];
    storageDescParams?: { name: string; value: string }[];
  };
  sampleData?: { headers: string[]; rows: (string | number | null)[][] };
  refresh: () => Promise<void>;
}

export function useTableDetails({
  connector,
  namespace,
  compute,
  database,
  table
}: UseTableDetailsArgs): TableDetailsState {
  const { t } = i18nReact.useTranslation();
  const [loading, setLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [overviewProps, setOverviewProps] = useState<TableDetailsState['overviewProps']>();
  const [sampleData, setSampleData] = useState<TableDetailsState['sampleData']>();
  const [detailsColumns, setDetailsColumns] = useState<TableDetailsState['detailsColumns']>([]);
  const [detailsProperties, setDetailsProperties] = useState<
    TableDetailsState['detailsProperties']
  >([]);
  const [detailsSections, setDetailsSections] = useState<TableDetailsState['detailsSections']>({});

  const fetchData = useCallback(async () => {
    setLoading(true);
    if (!database || !table || !connector || !namespace || !compute) {
      setOverviewProps(undefined);
      setSampleData(undefined);
      setDetailsColumns([]);
      setLoading(false);
      return;
    }
    try {
      const entry = await dataCatalog.getEntry({
        connector,
        namespace,
        compute,
        path: [database, table]
      });
      const analysis: Analysis = await entry.getAnalysis({ silenceErrors: true });
      const analysisDetails = (
        analysis as unknown as {
          details?: { properties?: Record<string, string>; stats?: Record<string, string> };
        }
      ).details;
      const isPartitioned = (analysis.partition_keys?.length || 0) > 0;
      const tableType = analysisDetails?.properties?.table_type;
      const createdBy = analysisDetails?.properties?.owner || 'hive';
      const createdTime = analysisDetails?.properties?.create_time;
      const createdTimeFormatted = createdTime
        ? (() => {
            const numeric = Number(createdTime);
            if (!isNaN(numeric) && isFinite(numeric)) {
              const ms = numeric < 1e12 ? numeric * 1000 : numeric;
              return formatTimestamp(new Date(ms));
            }
            const d = new Date(createdTime as unknown as string);
            return isNaN(d.getTime()) ? String(createdTime) : formatTimestamp(d);
          })()
        : undefined;
      // Determine if it's a view or table
      const isView = (analysis as unknown as { is_view?: boolean })?.is_view || entry.isView();
      const typeValue = isView ? t('View') : t('Table');

      const props = [
        { name: t('Type'), value: typeValue },
        { name: t('Partitioned'), value: isPartitioned ? t('Yes') : t('No') },
        { name: t('Managed'), value: tableType === 'MANAGED_TABLE' ? t('Yes') : t('No') },
        {
          name: t('Location'),
          value: (() => {
            const hdfsLink = (analysis as unknown as { hdfs_link?: string })?.hdfs_link;
            return hdfsLink || t('unknown location');
          })()
        },
        {
          name: t('Created'),
          value: createdTimeFormatted
            ? `${t('by')} ${createdBy} ${t('on')} ${createdTimeFormatted}`
            : '-'
        }
      ];
      const hdfsLink = (analysis as unknown as { hdfs_link?: string })?.hdfs_link;
      const detailStats = (analysis as unknown as { details?: { stats?: Record<string, string> } })
        ?.details?.stats;
      const stats = detailStats
        ? (() => {
            const files =
              (detailStats as Record<string, string>).num_files ||
              (detailStats as Record<string, string>).numFiles ||
              (detailStats as Record<string, string>).files;
            const rows =
              (detailStats as Record<string, string>).num_rows ||
              (detailStats as Record<string, string>).numRows ||
              (detailStats as Record<string, string>).rows;
            const rawTotalSize =
              (detailStats as Record<string, string>).total_size ||
              (detailStats as Record<string, string>).totalSize ||
              (detailStats as Record<string, string>).size;
            const totalSize = (() => {
              const n = Number(rawTotalSize);
              return !isNaN(n) && isFinite(n)
                ? formatBytes(n)
                : (rawTotalSize as unknown as string);
            })();
            const rawLastUpdated =
              (analysisDetails?.properties as Record<string, unknown>)?.transient_lastDdlTime ||
              (detailStats as Record<string, string>).last_modified_time ||
              (detailStats as Record<string, string>).lastModified ||
              (detailStats as Record<string, string>).lastUpdated;
            const lastUpdated = (() => {
              const n = Number(rawLastUpdated);
              if (!isNaN(n) && isFinite(n)) {
                const ms = n < 1e12 ? n * 1000 : n;
                return formatTimestamp(new Date(ms));
              }
              const d = new Date(rawLastUpdated as unknown as string);
              return isNaN(d.getTime())
                ? (rawLastUpdated as unknown as string)
                : formatTimestamp(d);
            })();
            const rawSchemaLastModified =
              (detailStats as Record<string, string>).last_modified_time ||
              (detailStats as Record<string, string>).lastModified;
            const schemaLastModifiedBy =
              (analysisDetails?.properties as Record<string, unknown>)?.last_modified_by ||
              (detailStats as Record<string, string>).last_modified_by;
            const schemaLastModified = rawSchemaLastModified
              ? (() => {
                  const n = Number(rawSchemaLastModified);
                  if (!isNaN(n) && isFinite(n)) {
                    const ms = n < 1e12 ? n * 1000 : n;
                    const timestamp = formatTimestamp(new Date(ms));
                    return schemaLastModifiedBy
                      ? `${timestamp} ${t('by')} ${schemaLastModifiedBy}`
                      : timestamp;
                  }
                  const d = new Date(rawSchemaLastModified as unknown as string);
                  const timestamp = isNaN(d.getTime())
                    ? String(rawSchemaLastModified)
                    : formatTimestamp(d);
                  return schemaLastModifiedBy
                    ? `${timestamp} ${t('by')} ${schemaLastModifiedBy}`
                    : timestamp;
                })()
              : undefined;
            return { files, rows, totalSize, lastUpdated, schemaLastModified };
          })()
        : undefined;
      const columnsForOverview = (analysis.cols || []).map(c => ({
        name: (c as unknown as { name: string }).name,
        type: (c as unknown as { type: string }).type,
        comment: (c as unknown as { comment?: string }).comment
      }));
      setOverviewProps({ properties: props, hdfsLink, stats });

      const rawProps = (analysisDetails?.properties || {}) as Record<string, unknown>;
      const baseInfo: { name: string; value: string }[] = [];
      const storageInfo: { name: string; value: string }[] = [];
      const storageDescParams: { name: string; value: string }[] = [];
      const tableParameters: { name: string; value: string }[] = [];

      const add = (arr: { name: string; value: string }[], name: string, value?: unknown) => {
        if (typeof value !== 'undefined' && value !== null && String(value) !== '') {
          arr.push({ name, value: String(value) });
        }
      };

      add(baseInfo, t('Database'), database || '');
      add(baseInfo, t('OwnerType'), rawProps.owner_type || rawProps.ownertype);
      add(baseInfo, t('Owner'), rawProps.owner);
      add(baseInfo, t('CreateTime'), createdTimeFormatted);
      const lastAccessRaw =
        (rawProps as Record<string, unknown>).last_access_time ||
        (rawProps as Record<string, unknown>).lastAccessTime ||
        'UNKNOWN';
      const lastAccessFormatted = (() => {
        if (lastAccessRaw === 'UNKNOWN') {
          return 'UNKNOWN';
        }
        const n = Number(lastAccessRaw as unknown as string);
        if (!isNaN(n) && isFinite(n)) {
          const ms = n < 1e12 ? n * 1000 : n;
          return formatTimestamp(new Date(ms));
        }
        const d = new Date(lastAccessRaw as unknown as string);
        return isNaN(d.getTime()) ? String(lastAccessRaw) : formatTimestamp(d);
      })();
      add(baseInfo, t('LastAccessTime'), lastAccessFormatted);
      add(baseInfo, t('Retention'), rawProps.retention);
      const hdfsLocation = (analysis as unknown as { hdfs_link?: string })?.hdfs_link;
      add(baseInfo, t('Location'), hdfsLocation);
      add(baseInfo, t('Table Type'), rawProps.table_type || rawProps.tableType);

      Object.keys(analysis.details.stats || {}).forEach(key => {
        const valueRaw = (analysis.details.stats as Record<string, unknown>)[key];
        const lower = key.toLowerCase();
        let value: string | undefined;
        if (lower.includes('size') || lower.includes('bytes') || lower.endsWith('length')) {
          const n = Number(valueRaw as unknown as string);
          if (!isNaN(n) && isFinite(n)) {
            value = formatBytes(n);
          }
        } else if (
          lower.includes('time') ||
          lower.includes('timestamp') ||
          lower.includes('date') ||
          lower.includes('modified')
        ) {
          const n = Number(valueRaw as unknown as string);
          if (!isNaN(n) && isFinite(n)) {
            const ms = n < 1e12 ? n * 1000 : n;
            value = formatTimestamp(new Date(ms));
          } else if (typeof valueRaw === 'string') {
            const d = new Date(valueRaw);
            if (!isNaN(d.getTime())) {
              value = formatTimestamp(d);
            }
          }
        }
        tableParameters.push({ name: key, value: String(value ?? valueRaw ?? '') });
      });
      [
        'transactional',
        'transactional_properties',
        'transient_lastDdlTime',
        'COLUMN_STATS_ACCURATE',
        'bucketing_version'
      ].forEach(key => {
        if (typeof rawProps[key] !== 'undefined') {
          tableParameters.push({ name: key, value: String(rawProps[key] as unknown as string) });
        }
      });

      add(
        storageInfo,
        t('SerDe Library'),
        (rawProps as Record<string, unknown>)['SerDe Library:'] ||
          (rawProps as Record<string, unknown>).serde_lib ||
          (rawProps as Record<string, unknown>).serdeLibName
      );
      add(
        storageInfo,
        t('InputFormat'),
        (rawProps as Record<string, unknown>).InputFormat ||
          (rawProps as Record<string, unknown>).input_format ||
          (rawProps as Record<string, unknown>).inputFormat
      );
      add(
        storageInfo,
        t('OutputFormat'),
        (rawProps as Record<string, unknown>).OutputFormat ||
          (rawProps as Record<string, unknown>).output_format ||
          (rawProps as Record<string, unknown>).outputFormat
      );
      add(
        storageInfo,
        t('Compressed'),
        (rawProps as Record<string, unknown>).compressed ? t('Yes') : t('No')
      );
      add(
        storageInfo,
        t('Num Buckets'),
        (rawProps as Record<string, unknown>).numBuckets ||
          (rawProps as Record<string, unknown>).num_buckets ||
          -1
      );
      add(
        storageInfo,
        t('Bucket Columns'),
        Array.isArray((rawProps as Record<string, unknown>).bucketCols)
          ? JSON.stringify((rawProps as Record<string, unknown>).bucketCols)
          : (rawProps as Record<string, unknown>).bucketCols || '[]'
      );
      add(
        storageInfo,
        t('Sort Columns'),
        Array.isArray((rawProps as Record<string, unknown>).sortCols)
          ? JSON.stringify((rawProps as Record<string, unknown>).sortCols)
          : (rawProps as Record<string, unknown>).sortCols || '[]'
      );

      if ((rawProps as Record<string, unknown>)['Storage Desc Params:']) {
        storageDescParams.push({
          name: t('serialization.format'),
          value: String((rawProps as Record<string, unknown>)['Storage Desc Params:'])
        });
      }

      const allProps = Object.keys(rawProps).map(key => ({
        name: key,
        value: String(rawProps[key] ?? '')
      }));
      setDetailsProperties(allProps);
      setDetailsSections({ baseInfo, tableParameters, storageInfo, storageDescParams });
      setDetailsColumns(columnsForOverview);

      // Only load sample data if it's not a view, or if views are allowed by config
      const config = getLastKnownConfig();
      const allowSampleDataFromViews = config?.hue_config?.allow_sample_data_from_views ?? false;

      if (!isView || allowSampleDataFromViews) {
        const sample = await entry.getSample({ silenceErrors: true });
        const headers = Array.isArray(sample.meta)
          ? (sample.meta as SampleMeta[]).map((m: SampleMeta) => m.name)
          : [];
        setSampleData({ headers, rows: sample.data || [] });
      } else {
        // Clear sample data for views when not allowed
        setSampleData(undefined);
      }
      const partitionKeyNames = new Set(
        (analysis.partition_keys || []).map(pk => pk.name).filter(Boolean)
      );
      const cols = (analysis.cols || []).map(c => ({
        name: (c as unknown as { name: string }).name,
        type: (c as unknown as { type: string }).type,
        comment: (c as unknown as { comment?: string }).comment,
        isPartitionKey: partitionKeyNames.has((c as unknown as { name: string }).name)
      }));
      setDetailsColumns(cols);
    } catch (err) {
      huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: t('Failed to load table data') });
    } finally {
      setLoading(false);
    }
  }, [connector, namespace, compute, database, table]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refresh = useCallback(async () => {
    if (!database || !table || !connector || !namespace || !compute) {
      return;
    }
    setIsRefreshing(true);
    try {
      const entry = await dataCatalog.getEntry({
        connector,
        namespace,
        compute,
        path: [database, table]
      });
      await entry.clearCache({ cascade: true, silenceErrors: true });

      // Refresh data without setting main loading state
      const analysis: Analysis = await entry.getAnalysis({ silenceErrors: true });
      const analysisDetails = (
        analysis as unknown as {
          details?: {
            stats?: TableStats;
            properties?: { name: string; value: string }[];
            hdfsLink?: string;
          };
        }
      )?.details;

      const children = await entry.getChildren({ silenceErrors: true });
      const columns = children.filter(child => child.isColumn());
      const columnDetails = columns.map(col => ({
        name: col.name || '',
        type: col.getType() || '',
        comment: col.comment || '',
        sample: '',
        isPartitionKey: col.isPartitionKey() || false
      }));

      // Update state
      setOverviewProps({
        properties: analysisDetails?.properties,
        stats: analysisDetails?.stats,
        hdfsLink: analysisDetails?.hdfsLink
      });
      setDetailsColumns(columnDetails);

      // Fetch additional details
      const detailsResponse = await post('/metastore/table/', {
        source_type: getConnectorIdOrType(connector) || 'hive',
        database: database,
        table: table
      });

      if (detailsResponse && typeof detailsResponse === 'object' && 'details' in detailsResponse) {
        const details = (detailsResponse as { details?: Record<string, unknown> }).details;
        if (details) {
          setDetailsProperties(Array.isArray(details.properties) ? details.properties : []);
          setDetailsSections({
            baseInfo: Array.isArray(details.partition_keys) ? details.partition_keys : [],
            tableParameters: Array.isArray(details.details) ? details.details : [],
            storageInfo: Array.isArray(details.storage) ? details.storage : [],
            storageDescParams: []
          });
        }
      }

      // Only fetch sample data if it's not a view, or if views are allowed by config
      const config = getLastKnownConfig();
      const allowSampleDataFromViews = config?.hue_config?.allow_sample_data_from_views ?? false;

      // Check if current table is a view by looking at properties
      const currentIsView =
        overviewProps?.properties?.find(p => p.name === t('Type'))?.value === t('View');

      if (!currentIsView || allowSampleDataFromViews) {
        // Fetch sample data
        const sampleResponse = await post('/metastore/table/', {
          source_type: getConnectorIdOrType(connector) || 'hive',
          database: database,
          table: table,
          sample: true
        });

        if (sampleResponse && typeof sampleResponse === 'object' && 'sample' in sampleResponse) {
          const sample = (sampleResponse as { sample?: Record<string, unknown> }).sample;
          if (sample && typeof sample === 'object' && 'headers' in sample && 'rows' in sample) {
            setSampleData(sample as { headers: string[]; rows: (string | number | null)[][] });
          }
        }
      } else {
        // Clear sample data for views when not allowed
        setSampleData(undefined);
      }
    } catch (error) {
      console.error('Error during refresh:', error);
    } finally {
      setIsRefreshing(false);
    }
  }, [connector, namespace, compute, database, table]);

  return {
    loading,
    isRefreshing,
    overviewProps,
    detailsColumns,
    detailsProperties,
    detailsSections,
    sampleData,
    refresh
  };
}
