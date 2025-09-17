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
import { getLastKnownConfig } from '../../../config/hueConfig';
import type { Analysis, SampleMeta } from '../../../catalog/DataCatalogEntry';
import type { Connector, Compute, Namespace } from '../../../config/types';

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
  partitionCount?: number;
  rawAnalysis?: Analysis;
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
  const [partitionCount, setPartitionCount] = useState<number | undefined>(undefined);
  const [rawAnalysis, setRawAnalysis] = useState<Analysis | undefined>(undefined);

  const fetchData = useCallback(async () => {
    setLoading(true);
    if (!database || !table || !connector || !namespace || !compute) {
      setOverviewProps(undefined);
      setSampleData(undefined);
      setDetailsColumns([]);
      setPartitionCount(undefined);
      setRawAnalysis(undefined);
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
      setRawAnalysis(analysis);
      const analysisDetails = (
        analysis as unknown as {
          details?: { properties?: Record<string, string>; stats?: Record<string, string> };
        }
      ).details;
      const isPartitioned = (analysis.partition_keys?.length || 0) > 0;

      // Note: Partition count will be fetched separately to avoid timing issues

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
      ].map(prop => ({ ...prop, value: prop.value || '-' }));
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
      // Normalize columns as some connectors (e.g. PostgreSQL) wrap column defs in nested arrays
      const flattenColumns = (
        cols: unknown
      ): { name?: string; type?: string; comment?: string }[] => {
        const flat: { name?: string; type?: string; comment?: string }[] = [];
        const pushCol = (item: unknown): void => {
          if (Array.isArray(item)) {
            item.forEach(pushCol);
          } else if (item && typeof item === 'object') {
            const obj = item as { name?: string; type?: string; comment?: string };
            flat.push({ name: obj.name, type: obj.type, comment: obj.comment });
          }
        };
        pushCol(cols);
        return flat;
      };

      const normalizedCols = flattenColumns((analysis as unknown as { cols?: unknown }).cols || []);

      const columnsForOverview = normalizedCols.map(c => ({
        name: c.name || '',
        type: c.type || '',
        comment: c.comment
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

      // Merge in legacy section rows from analysis.properties for Detailed Table Information and Storage Information
      type LegacyProp = { col_name?: string; data_type?: string; comment?: string };
      const legacyProps = ((analysis as unknown as { properties?: LegacyProp[] }).properties ||
        []) as LegacyProp[];
      const isHeader = (p?: LegacyProp): boolean => (p?.col_name || '').trim().startsWith('#');
      const normalizeName = (name: string): string => name.trim().replace(/:$/, '').toLowerCase();
      const friendlyName = (name: string): string => {
        const map: Record<string, string> = {
          'serde library': t('SerDe Library'),
          inputformat: t('InputFormat'),
          outputformat: t('OutputFormat'),
          compressed: t('Compressed'),
          'num buckets': t('Num Buckets'),
          'bucket columns': t('Bucket Columns'),
          'sort columns': t('Sort Columns')
        };
        const key = normalizeName(name);
        return map[key] || name.replace(/:$/, '').trim();
      };
      const collectSection = (header: string): { name: string; value: string }[] => {
        const out: { name: string; value: string }[] = [];
        const idx = legacyProps.findIndex(
          p => (p.col_name || '').toLowerCase() === header.toLowerCase()
        );
        if (idx === -1) {
          return out;
        }
        for (let i = idx + 1; i < legacyProps.length; i++) {
          const row = legacyProps[i];
          if (isHeader(row)) {
            break;
          }
          const col = String(row.col_name || '').trim();
          if (normalizeName(col).startsWith('table parameters')) {
            // Stop before the Table Parameters block; those go in their own table
            break;
          }
          let name: string = '';
          let value: string = '';
          if (col) {
            name = friendlyName(col);
            value = String((row.data_type ?? row.comment ?? '') as unknown as string);
          } else {
            // Rows where the property name is in data_type and value in comment
            name = friendlyName(String(row.data_type || ''));
            value = String((row.comment ?? '') as unknown as string);
          }
          if (name || value) {
            out.push({ name: name || '\u00A0', value });
          }
        }
        return out;
      };

      const mergeUnique = (
        target: { name: string; value: string }[],
        more: { name: string; value: string }[]
      ) => {
        const existing = new Set(target.map(p => normalizeName(p.name)));
        more.forEach(p => {
          const key = normalizeName(p.name);
          if (!existing.has(key)) {
            target.push(p);
            existing.add(key);
          }
        });
      };

      // Detailed Table Information
      mergeUnique(baseInfo, collectSection('# Detailed Table Information'));

      // Fallback: Some legacy analyzers expose important flags (e.g., COLUMN_STATS_ACCURATE)
      // as rows with empty col_name and the key in data_type with value in comment. If for any
      // reason the collectSection missed them, ensure we add them explicitly here.
      const legacyStatsRow = (legacyProps || []).find(
        p => normalizeName(String(p.data_type || '')) === 'column_stats_accurate'
      );
      if (legacyStatsRow) {
        let value: string;
        if (typeof legacyStatsRow.comment !== 'undefined') {
          value =
            typeof legacyStatsRow.comment === 'string'
              ? legacyStatsRow.comment
              : JSON.stringify(legacyStatsRow.comment);
        } else {
          value = String(legacyStatsRow.data_type || '');
        }
        baseInfo.push({ name: 'COLUMN_STATS_ACCURATE', value });
      }

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

      // Storage Information (legacy)
      mergeUnique(storageInfo, collectSection('# Storage Information'));

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
      const cleanedBaseInfo = baseInfo.filter(p => {
        const key = normalizeName(p.name);
        const val = String(p.value || '').trim();
        return !(key === 'table parameters' && val === '');
      });
      // Debugging aid for tests; safe no-op in production
      // eslint-disable-next-line no-console
      console.log('[useTableDetails] baseInfo', baseInfo);
      setDetailsSections({
        baseInfo: cleanedBaseInfo,
        tableParameters,
        storageInfo,
        storageDescParams
      });
      setDetailsColumns(columnsForOverview);

      // Only load sample data if it's not a view, or if views are allowed by config
      const config = getLastKnownConfig();
      const allowSampleDataFromViews = config?.hue_config?.allow_sample_data_from_views ?? false;

      if (!isView || allowSampleDataFromViews) {
        const sample = await entry.getSample({ silenceErrors: true });
        const headers = Array.isArray(sample.meta)
          ? (sample.meta as SampleMeta[]).map((m: SampleMeta) => m.name)
          : [];
        setSampleData({
          headers,
          rows: (sample.data || []) as (string | number | null)[][]
        });
      } else {
        // Clear sample data for views when not allowed
        setSampleData(undefined);
      }
      const partitionKeyNames = new Set(
        (analysis.partition_keys || []).map(pk => pk.name).filter(Boolean)
      );
      const cols = normalizedCols.map(c => ({
        name: c.name || '',
        type: c.type || '',
        comment: c.comment,
        isPartitionKey: partitionKeyNames.has(String(c.name || ''))
      }));
      setDetailsColumns(cols);
    } catch (err) {
      setRawAnalysis(undefined);
      huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: t('Failed to load table data') });
    } finally {
      setLoading(false);
    }
  }, [connector, namespace, compute, database, table]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Separate effect for fetching partition count to avoid timing issues
  useEffect(() => {
    const fetchPartitionCount = async () => {
      if (!database || !table || !connector || !namespace || !compute) {
        setPartitionCount(undefined);
        return;
      }

      try {
        const entry = await dataCatalog.getEntry({
          connector,
          namespace,
          compute,
          path: [database, table]
        });
        const analysis = await entry.getAnalysis({ silenceErrors: true });
        const isPartitioned = (analysis.partition_keys?.length || 0) > 0;

        if (isPartitioned) {
          const partitions = await entry.getPartitions();
          const count = (partitions?.partition_values_json || []).length;
          setPartitionCount(count);
        } else {
          setPartitionCount(undefined);
        }
      } catch (err) {
        setPartitionCount(undefined);
      }
    };

    fetchPartitionCount();
  }, [connector, namespace, compute, database, table]);

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

      // Re-fetch all data using the same logic as initial load
      await fetchData();
    } catch (error) {
      console.error('Error during refresh:', error);
      // Don't show error notification for refresh failures as they're often recoverable
      // and the user can still see the existing data
    } finally {
      setIsRefreshing(false);
    }
  }, [connector, namespace, compute, database, table, fetchData]);

  return {
    loading,
    isRefreshing,
    overviewProps,
    detailsColumns,
    detailsProperties,
    detailsSections,
    sampleData,
    partitionCount,
    rawAnalysis,
    refresh
  };
}
