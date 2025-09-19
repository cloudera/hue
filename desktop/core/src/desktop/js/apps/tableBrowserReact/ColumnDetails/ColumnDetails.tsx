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

import React, { useMemo, useState } from 'react';
import DataVersionsIcon from '@cloudera/cuix-core/icons/react/DataVersionsIcon';
import Loading from 'cuix/dist/components/Loading';
import Switch from 'cuix/dist/components/Switch';
import Button from 'cuix/dist/components/Button';
import CopyClipboardIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';
import PageHeader from '../sharedComponents/PageHeader';
import MetaDataDisplay from '../sharedComponents/MetaDataDisplay';
import PrettyStructDisplay from '../sharedComponents/PrettyStructDisplay';
import './ColumnDetails.scss';
import { i18nReact } from '../../../utils/i18nReact';
import type { Connector, Namespace, Compute } from '../../../config/types';
import type { TableDetailsState } from '../hooks/useTableDetails';
import SampleGrid from '../TableDetails/SampleTab/SampleGrid';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import decodeHtmlEntities from '../../../utils/strings/decodeHtmlEntities';

export interface ColumnDetailsProps {
  sourceType?: string;
  database: string;
  table: string;
  column: string;
  fields?: string[];
  connector: Connector | null;
  namespace: Namespace | null;
  compute: Compute | null;
  tableDetails: TableDetailsState;
  onBackToTable: () => void;
  onOpenField?: (nextFields: string[]) => void;
  // Breadcrumb navigation callbacks (optional). If not provided, fall back to onBackToTable where applicable
  onClickDataSources?: () => void;
  onClickDatabases?: () => void;
  onClickDatabase?: (database: string) => void;
  onClickTable?: (table: string) => void;
}

const ColumnDetails = ({
  sourceType,
  database,
  table,
  column,
  fields = [],
  tableDetails,
  onBackToTable,
  onOpenField,
  onClickDataSources,
  onClickDatabases,
  onClickDatabase,
  onClickTable
}: ColumnDetailsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const { loading: loadingData, isRefreshing, detailsColumns, sampleData } = tableDetails;

  const columnMeta = useMemo(() => {
    return detailsColumns.find(c => c.name === column);
  }, [detailsColumns, column]);

  const columnSampleData = useMemo(() => {
    if (!sampleData?.headers || !sampleData?.rows) {
      return undefined;
    }
    let idx = sampleData.headers.indexOf(column);
    if (idx === -1) {
      idx = sampleData.headers.findIndex(h => h.toLowerCase() === column.toLowerCase());
    }
    if (idx === -1) {
      idx = sampleData.headers.findIndex(h => h.includes(column) || column.includes(h));
    }
    if (idx === -1) {
      return { headers: [column], rows: [] as (string | number | null)[][] };
    }
    const rows = sampleData.rows.map(r => [decodeHtmlEntities(r[idx]) as string | number | null]);
    return { headers: [column], rows };
  }, [sampleData, column]);

  const columnType = useMemo(() => columnMeta?.type || '', [columnMeta]);

  const isStruct = useMemo(
    () => (columnMeta?.type || '').toLowerCase().startsWith('struct<'),
    [columnMeta]
  );

  const handleCopyTypeToClipboard = async (): Promise<void> => {
    if (columnType) {
      try {
        await navigator.clipboard.writeText(columnType);
      } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = columnType;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }
    }
  };

  // Toggle for flattened vs top-level view
  const [flattened, setFlattened] = useState(false);

  // Parse struct fields (including nested) into dotted paths: struct<a:int,b:struct<c:int>> => a, b.c
  const allStructFields: { name: string; type: string }[] = useMemo(() => {
    const type = (columnMeta?.type || '').trim();
    if (!type.toLowerCase().startsWith('struct<')) {
      return [];
    }
    const splitTopLevel = (text: string): string[] => {
      const out: string[] = [];
      let depth = 0;
      let buf = '';
      for (let i = 0; i < text.length; i++) {
        const ch = text[i];
        if (ch === '<') {
          depth += 1;
          buf += ch;
          continue;
        }
        if (ch === '>') {
          depth = Math.max(0, depth - 1);
          buf += ch;
          continue;
        }
        if (ch === ',' && depth === 0) {
          out.push(buf.trim());
          buf = '';
          continue;
        }
        buf += ch;
      }
      if (buf.trim()) {
        out.push(buf.trim());
      }
      return out;
    };

    const parseStructInner = (innerType: string, prefix = ''): { name: string; type: string }[] => {
      const result: { name: string; type: string }[] = [];
      // Split by top-level commas (ignore commas inside nested <>)
      const parts = splitTopLevel(innerType);
      for (const rawPart of parts) {
        const part = rawPart.trim();
        if (!part) {
          continue;
        }
        const colonIdx = part.indexOf(':');
        const fieldName = colonIdx === -1 ? part : part.slice(0, colonIdx).trim();
        const fieldType = colonIdx === -1 ? '' : part.slice(colonIdx + 1).trim();
        const fullName = prefix ? `${prefix}.${fieldName}` : fieldName;
        if (fieldType.toLowerCase().startsWith('struct<')) {
          // Include the container struct field itself so top-level mode can display it
          result.push({ name: fullName, type: fieldType });
          const inner = fieldType.slice(fieldType.indexOf('<') + 1, fieldType.lastIndexOf('>'));
          result.push(...parseStructInner(inner, fullName));
        } else {
          result.push({ name: fullName, type: fieldType });
        }
      }
      return result;
    };
    const inner = type.slice(type.indexOf('<') + 1, type.lastIndexOf('>'));
    return parseStructInner(inner);
  }, [columnMeta]);

  // Current path (fields segments) as dotted prefix
  const currentPath = fields.join('.');

  // Filter field list for current path and map to relative names
  const structFields = useMemo(() => {
    if (!currentPath) {
      return allStructFields;
    }
    const prefix = `${currentPath}.`;
    return allStructFields
      .filter(f => f.name === currentPath || f.name.startsWith(prefix))
      .map(f => ({ name: f.name === currentPath ? '' : f.name.slice(prefix.length), type: f.type }))
      .filter(f => f.name);
  }, [allStructFields, currentPath]);

  // Only direct children for the current path (exclude grandchildren and deeper)
  const directStructFields = useMemo(() => {
    if (!currentPath) {
      // Root level: direct children have no dot in their full path
      return allStructFields.filter(f => !f.name.includes('.'));
    }
    const prefix = `${currentPath}.`;
    // Keep entries that start with the prefix and have no additional dot after the prefix
    return allStructFields
      .filter(f => f.name.startsWith(prefix) && !f.name.slice(prefix.length).includes('.'))
      .map(f => ({ name: f.name.slice(prefix.length), type: f.type }));
  }, [allStructFields, currentPath]);

  const hasStructChildren = useMemo(
    () => directStructFields.some(f => (f.type || '').toLowerCase().startsWith('struct<')),
    [directStructFields]
  );

  // Extract sample values for struct fields from each row's struct cell (supports nested paths)
  const structFieldSamples = useMemo(() => {
    if (!isStruct || !columnSampleData?.rows?.length) {
      return {} as Record<string, Array<string | number | null>>;
    }
    const samples: Record<string, Array<string | number | null>> = {};
    const tryParse = (val: unknown): Record<string, unknown> | null => {
      if (val == null) {
        return null;
      }
      if (typeof val === 'object') {
        return (val as Record<string, unknown>) || null;
      }
      const s = String(val);
      // Try JSON first
      if (/^\s*[\[{]/.test(s)) {
        try {
          const parsed = JSON.parse(s);
          return parsed && typeof parsed === 'object' ? (parsed as Record<string, unknown>) : null;
        } catch {
          // fallthrough
        }
      }
      // Fallback simple parser: key:value pairs separated by commas at top level
      const obj: Record<string, unknown> = {};
      s.split(/,(?![^\[]*\]|[^\(]*\)|[^\{]*\})/g).forEach(pair => {
        const [k, ...rv] = pair.split(':');
        if (k) {
          obj[k.trim().replace(/^['\"]|['\"]$/g, '')] = rv
            .join(':')
            .trim()
            .replace(/^['\"]|['\"]$/g, '');
        }
      });
      return Object.keys(obj).length ? obj : null;
    };

    const flatten = (
      obj: Record<string, unknown>,
      prefix = ''
    ): Record<string, string | number> => {
      const out: Record<string, string | number> = {};
      Object.keys(obj).forEach(key => {
        const val = obj[key] as unknown;
        const path = prefix ? `${prefix}.${key}` : key;
        if (val && typeof val === 'object' && !Array.isArray(val)) {
          Object.assign(out, flatten(val as Record<string, unknown>, path));
        } else if (val !== undefined && val !== null) {
          const outVal: string | number =
            typeof val === 'object' ? JSON.stringify(val) : (val as string | number);
          out[path] = outVal;
        }
      });
      return out;
    };

    for (const row of columnSampleData.rows) {
      const cell = row[0];
      const decoded = decodeHtmlEntities(cell);
      const obj = tryParse(decoded);
      if (!obj) {
        continue;
      }
      const flat = flatten(obj);
      structFields.forEach(f => {
        const fq = currentPath ? `${currentPath}.${f.name}` : f.name;
        const v = flat[fq] as unknown;
        if (!samples[f.name]) {
          samples[f.name] = [];
        }
        if (v !== undefined && v !== null) {
          samples[f.name].push(
            (typeof v === 'object' ? JSON.stringify(v) : (v as string | number)) as string | number
          );
        }
      });
    }
    return samples;
  }, [isStruct, columnSampleData, structFields]);

  const structRows = useMemo(() => {
    if (!isStruct) {
      return [] as Array<{
        key: string;
        field: string;
        type: string;
        sample1?: string | number;
        sample2?: string | number;
      }>;
    }
    if (flattened) {
      return structFields
        .filter(f => !(f.type || '').toLowerCase().startsWith('struct<'))
        .map(f => {
          const vals = structFieldSamples[f.name] || [];
          return {
            key: f.name,
            field: f.name,
            type: f.type,
            sample1: vals[0] as string | number | undefined,
            sample2: vals[1] as string | number | undefined
          };
        });
    }
    // Top-level: only direct children
    const topLevel = directStructFields.map(f => {
      const vals = structFieldSamples[f.name] || [];
      return {
        key: f.name,
        field: f.name,
        type: f.type,
        sample1: vals[0] as string | number | undefined,
        sample2: vals[1] as string | number | undefined
      };
    });
    return topLevel;
  }, [isStruct, directStructFields, structFieldSamples, flattened]);

  const structColumns: PaginatedColumnProps<{
    key: string;
    field: string;
    type: string;
    sample1?: string | number;
    sample2?: string | number;
  }>[] = useMemo(() => {
    const getBaseType = (type: string): string => {
      const lower = (type || '').trim().toLowerCase();
      if (!lower) {
        return '';
      }
      if (lower.startsWith('struct<')) {
        return 'struct';
      }
      if (lower.startsWith('array<')) {
        return 'array';
      }
      if (lower.startsWith('map<')) {
        return 'map';
      }
      const match = lower.match(/^([a-z_]+)/);
      return match ? match[1] : lower;
    };

    type TypeCategory = 'number' | 'text' | 'boolean' | 'time' | 'json' | 'complex' | 'other';

    const categorizeType = (type: string): TypeCategory => {
      const base = getBaseType(type);
      if (!base) {
        return 'other';
      }
      if (
        [
          'int',
          'integer',
          'bigint',
          'smallint',
          'tinyint',
          'float',
          'double',
          'real',
          'decimal',
          'numeric'
        ].includes(base)
      ) {
        return 'number';
      }
      if (['string', 'varchar', 'char', 'binary', 'varbinary'].includes(base)) {
        return 'text';
      }
      if (base === 'boolean') {
        return 'boolean';
      }
      if (['date', 'timestamp', 'timestamptz', 'interval'].includes(base)) {
        return 'time';
      }
      if (base === 'json') {
        return 'json';
      }
      if (['struct', 'array', 'map'].includes(base)) {
        return 'complex';
      }
      return 'other';
    };

    return [
      {
        title: t('Field'),
        dataIndex: 'field',
        key: 'field',
        sorter: true,
        render: (name: string, record: { field: string; type: string }) => {
          const isSubStruct = (record.type || '').toLowerCase().startsWith('struct<');
          if (!onOpenField || !isSubStruct) {
            return name;
          }
          const next = [...fields, name];
          return (
            <button
              type="button"
              className="link-like"
              onClick={() => onOpenField(next)}
              style={{
                padding: 0,
                border: 0,
                background: 'none',
                color: '#1890ff',
                cursor: 'pointer'
              }}
            >
              {name}
            </button>
          );
        }
      },
      {
        title: t('Type'),
        dataIndex: 'type',
        key: 'type',
        sorter: true,
        render: (v: string) => {
          const isNestedStruct = v.toLowerCase().startsWith('struct<');
          if (isNestedStruct) {
            return <PrettyStructDisplay structType={v} compact={true} />;
          }
          const category = categorizeType(v);
          return (
            <span
              className={`hue-type-label hue-type--${category}`}
              title={v}
              aria-label={`${t('Type')}: ${v}`}
              style={{ whiteSpace: 'normal', wordBreak: 'break-word' }}
            >
              {v}
            </span>
          );
        }
      },
      {
        title: t('Sample'),
        dataIndex: 'sample1',
        key: 'sample1',
        render: (v?: string | number) =>
          v != null ? <span title={String(v)}>{String(v)}</span> : ''
      },
      {
        title: '',
        dataIndex: 'sample2',
        key: 'sample2',
        render: (v?: string | number) =>
          v != null ? <span title={String(v)}>{String(v)}</span> : ''
      }
    ];
  }, [t]);

  const titleName = (fields && fields.length ? fields[fields.length - 1] : column) || column;

  return (
    <div className="hue-column-details">
      <PageHeader
        title={titleName}
        icon={<DataVersionsIcon />}
        onRefresh={async () => {
          await tableDetails.refresh();
        }}
        loading={loadingData}
        isRefreshing={isRefreshing}
        sourceType={sourceType}
        database={database}
        table={table}
        column={column}
        fields={fields}
        onClickColumn={() => onOpenField && onOpenField([])}
        onClickField={next => onOpenField && onOpenField(next)}
        onClickTable={() => (onClickTable ? onClickTable(table) : onBackToTable())}
        onClickDatabases={() => (onClickDatabases ? onClickDatabases() : onBackToTable())}
        onClickDatabase={() => (onClickDatabase ? onClickDatabase(database) : onBackToTable())}
        onClickDataSources={onClickDataSources}
      />

      <div className="hue-table-browser__header-with-actions">
        <h3 className="hue-h3">{t('Column details')}</h3>
      </div>

      <div className="hue-column-details__meta">
        <MetaDataDisplay
          groups={[
            {
              items: [
                { label: t('Name'), value: column, key: 'name' },
                {
                  label: t('Type'),
                  value: isStruct ? 'struct' : columnType,
                  key: 'type'
                },
                {
                  label: t('Description'),
                  value: (columnMeta?.comment as unknown as string) || t('No description'),
                  key: 'description'
                }
              ]
            }
          ]}
        />
      </div>

      {isStruct ? (
        <div className="hue-column-details__type-panel" style={{ marginBottom: 16 }}>
          <div className="hue-column-details__type-title-bar">
            {t('Type definition')}
            <div className="hue-column-details__type-action-group">
              <Button onClick={handleCopyTypeToClipboard} title={t('Copy type to clipboard')}>
                <CopyClipboardIcon /> {t('Copy')}
              </Button>
            </div>
          </div>
          <div
            className="hue-column-details__type-content"
            role="region"
            aria-label={t('Column type')}
          >
            <PrettyStructDisplay structType={columnType} />
          </div>
        </div>
      ) : null}

      {isStruct ? (
        <>
          <div className="hue-table-browser__header-with-actions">
            <h3 className="hue-h3">{t('Fields')}</h3>
            {hasStructChildren && (
              <div className="hue-column-details__flatten">
                <Switch checked={flattened} onChange={() => setFlattened(prev => !prev)} />
                <span>{t('Show flattened')}</span>
              </div>
            )}
          </div>
          <PaginatedTable<{
            key: string;
            field: string;
            type: string;
            sample1?: string | number;
            sample2?: string | number;
          }>
            data={structRows}
            columns={structColumns}
            rowKey="key"
            rowClassName={record => {
              if (!flattened) {
                return '';
              }
              const topLevel = (record.field || '').split('.')[0];
              // Alternate every second group
              const groupIndex = Array.from(
                new Set(structRows.map(r => (r.field || '').split('.')[0]))
              ).indexOf(topLevel);
              return groupIndex % 2 === 1 ? 'struct-group--alt' : '';
            }}
            pagination={{
              pageStats: {
                pageNumber: 1,
                totalPages: 1,
                pageSize: Math.max(structRows.length, 1),
                totalSize: structRows.length
              }
            }}
          />
        </>
      ) : (
        <>
          <div className="hue-table-browser__header-with-actions">
            <h3 className="hue-h3">{t('Sample values')}</h3>
          </div>
          <Loading spinning={!sampleData}>
            {!sampleData ? null : (
              <SampleGrid
                data={columnSampleData}
                isRefreshing={isRefreshing}
                database={database}
                table={table}
              />
            )}
          </Loading>
        </>
      )}
    </div>
  );
};

export default ColumnDetails;
