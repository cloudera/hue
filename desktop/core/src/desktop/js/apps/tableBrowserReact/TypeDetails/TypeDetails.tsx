// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useMemo, useState } from 'react';
import DataVersionsIcon from '@cloudera/cuix-core/icons/react/DataVersionsIcon';
import Switch from 'cuix/dist/components/Switch';
import Loading from 'cuix/dist/components/Loading';

import { i18nReact } from '../../../utils/i18nReact';
import type { TableDetailsState } from '../hooks/useTableDetails';

import PageHeader from '../sharedComponents/PageHeader';
import MetaDataDisplay from '../sharedComponents/MetaDataDisplay';
import PrettyStructDisplay from '../sharedComponents/PrettyStructDisplay';
import SampleGrid from '../TableDetails/SampleTab/SampleGrid';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';

import decodeHtmlEntities from '../../../utils/strings/decodeHtmlEntities';

import './TypeDetails.scss';

export interface TypeDetailsProps {
  sourceType?: string;
  database: string;
  table: string;
  column: string;
  fields: string[]; // path into the column type (e.g., ["a","b"])
  tableDetails: TableDetailsState;
  onOpenField?: (nextFields: string[]) => void;
  onClickDataSources?: () => void;
  onClickDatabases?: () => void;
  onClickDatabase?: (database: string) => void;
  onClickTable?: (table: string) => void;
}

type FieldRow = {
  key: string;
  field: string;
  type: string;
  sample1?: string | number;
  sample2?: string | number;
};

const TypeDetails = ({
  sourceType,
  database,
  table,
  column,
  fields,
  tableDetails,
  onOpenField,
  onClickDataSources,
  onClickDatabases,
  onClickDatabase,
  onClickTable
}: TypeDetailsProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const { isRefreshing, loading, detailsColumns, sampleData } = tableDetails;

  const columnMeta = useMemo(
    () => detailsColumns.find(c => c.name === column),
    [detailsColumns, column]
  );
  const columnType = useMemo(() => (columnMeta?.type || '').trim(), [columnMeta]);

  const [flattened, setFlattened] = useState(false);

  // Helpers shared with other pages
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

  // Walk the nested type and return the target type at `fields` path
  const targetType: string = useMemo(() => {
    let current = columnType.trim();
    if (!fields.length) {
      return current;
    }
    const stepIntoStruct = (src: string, segment: string): string | undefined => {
      const lower = src.toLowerCase();
      if (!lower.startsWith('struct<')) {
        return undefined;
      }
      const inner = src.slice(src.indexOf('<') + 1, src.lastIndexOf('>'));
      // Split top-level fields
      let depth = 0;
      let buf = '';
      const parts: string[] = [];
      for (let i = 0; i < inner.length; i++) {
        const ch = inner[i];
        if (ch === '<') {
          depth++;
        } else if (ch === '>') {
          depth = Math.max(0, depth - 1);
        } else if (ch === ',' && depth === 0) {
          parts.push(buf.trim());
          buf = '';
          continue;
        }
        buf += ch;
      }
      if (buf.trim()) {
        parts.push(buf.trim());
      }
      // Find the segment
      for (const p of parts) {
        const colon = p.indexOf(':');
        const name = (colon === -1 ? p : p.slice(0, colon)).trim();
        const typ = (colon === -1 ? '' : p.slice(colon + 1)).trim();
        if (name === segment) {
          return typ;
        }
      }
      return undefined;
    };

    for (const seg of fields) {
      const next = stepIntoStruct(current, seg);
      if (!next) {
        return current; // fallback to last known
      }
      current = next;
    }
    return current;
  }, [columnType, fields]);

  const typeCategory = useMemo(() => categorizeType(targetType), [targetType]);
  const typeBase = useMemo(() => getBaseType(targetType), [targetType]);
  const typePathLabel = useMemo(() => (fields && fields.length ? fields.join('.') : ''), [fields]);
  const titleName = useMemo(
    () => (fields && fields.length ? fields[fields.length - 1] : column),
    [fields, column]
  );

  // Whether direct children include nested structs (used to decide showing the flatten toggle)
  const hasStructChildren = useMemo(() => {
    if (typeBase !== 'struct') {
      return false;
    }
    const inner = targetType.slice(targetType.indexOf('<') + 1, targetType.lastIndexOf('>'));
    let depth = 0;
    let buf = '';
    const parts: string[] = [];
    for (let i = 0; i < inner.length; i++) {
      const ch = inner[i];
      if (ch === '<') {
        depth++;
      } else if (ch === '>') {
        depth = Math.max(0, depth - 1);
      } else if (ch === ',' && depth === 0) {
        parts.push(buf.trim());
        buf = '';
        continue;
      }
      buf += ch;
    }
    if (buf.trim()) {
      parts.push(buf.trim());
    }
    return parts.some(p => {
      const idx = p.indexOf(':');
      const ftype = (idx === -1 ? '' : p.slice(idx + 1)).trim().toLowerCase();
      return ftype.startsWith('struct<');
    });
  }, [typeBase, targetType]);

  // Build rows for struct fields (direct children or flattened)
  const structRows: FieldRow[] = useMemo(() => {
    const lower = targetType.toLowerCase();
    if (!lower.startsWith('struct<')) {
      return [];
    }
    const inner = targetType.slice(targetType.indexOf('<') + 1, targetType.lastIndexOf('>'));
    // Helper to split top-level entries
    const splitTop = (text: string): string[] => {
      const out: string[] = [];
      let depth = 0;
      let buf = '';
      for (let i = 0; i < text.length; i++) {
        const ch = text[i];
        if (ch === '<') {
          depth++;
        } else if (ch === '>') {
          depth = Math.max(0, depth - 1);
        } else if (ch === ',' && depth === 0) {
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
    const parts = splitTop(inner);
    const direct: FieldRow[] = [];
    for (const p of parts) {
      const idx = p.indexOf(':');
      const fname = (idx === -1 ? p : p.slice(0, idx)).trim();
      const ftype = (idx === -1 ? '' : p.slice(idx + 1)).trim();
      direct.push({ key: fname, field: fname, type: ftype });
    }
    if (flattened) {
      // Expand nested structs into dot notation with a quick DFS
      const out: FieldRow[] = [];
      const dfs = (name: string, t: string) => {
        const tl = (t || '').toLowerCase();
        if (!tl.startsWith('struct<')) {
          out.push({ key: name, field: name, type: t });
          return;
        }
        const inner2 = t.slice(t.indexOf('<') + 1, t.lastIndexOf('>'));
        for (const part of splitTop(inner2)) {
          const cidx = part.indexOf(':');
          const cn = (cidx === -1 ? part : part.slice(0, cidx)).trim();
          const ct = (cidx === -1 ? '' : part.slice(cidx + 1)).trim();
          dfs(`${name}.${cn}`, ct);
        }
      };
      for (const row of direct) {
        dfs(row.field, row.type);
      }
      return out.filter(r => !getBaseType(r.type).startsWith('struct'));
    }
    return direct;
  }, [targetType, flattened]);

  // Sample values for struct fields
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

  const structFieldSamples = useMemo(() => {
    if (!targetType.toLowerCase().startsWith('struct<') || !columnSampleData?.rows?.length) {
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
      if (/^\s*[\[{]/.test(s)) {
        try {
          const parsed = JSON.parse(s);
          return parsed && typeof parsed === 'object' ? (parsed as Record<string, unknown>) : null;
        } catch {
          // noop
        }
      }
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
      const obj = tryParse(cell);
      if (!obj) {
        continue;
      }
      const flat = flatten(obj);
      structRows.forEach(f => {
        const fq = typePathLabel ? `${typePathLabel}.${f.field}` : f.field;
        const v = flat[fq] as unknown;
        if (!samples[f.field]) {
          samples[f.field] = [];
        }
        if (v !== undefined && v !== null) {
          samples[f.field].push(
            (typeof v === 'object' ? JSON.stringify(v) : (v as string | number)) as string | number
          );
        }
      });
    }
    return samples;
  }, [targetType, columnSampleData, structRows, typePathLabel]);

  const rowsWithSamples: FieldRow[] = useMemo(() => {
    if (!targetType.toLowerCase().startsWith('struct<')) {
      return [];
    }
    return (structRows || []).map(r => {
      const vals = (structFieldSamples[r.field] || []) as Array<string | number>;
      return {
        ...r,
        sample1: vals[0],
        sample2: vals[1]
      };
    });
  }, [structRows, structFieldSamples, targetType]);

  const columnsDef: PaginatedColumnProps<FieldRow>[] = useMemo(
    () => [
      {
        title: t('Field'),
        dataIndex: 'field',
        key: 'field',
        sorter: true,
        render: (name: string, record: FieldRow) => {
          const base = getBaseType(record.type);
          if (base === 'struct' && onOpenField) {
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
          return name;
        }
      },
      {
        title: t('Type'),
        dataIndex: 'type',
        key: 'type',
        sorter: true,
        render: (v: string) => {
          const base = getBaseType(v);
          if (base === 'struct') {
            return <PrettyStructDisplay structType={v} compact={true} />;
          }
          const category = categorizeType(v);
          return (
            <span
              className={`hue-type-label hue-type--${category}`}
              title={v}
              aria-label={`${t('Type')}: ${base}`}
            >
              {base}
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
    ],
    [t, fields, onOpenField]
  );

  return (
    <div className="hue-type-details">
      <PageHeader
        title={titleName}
        icon={<DataVersionsIcon />}
        onRefresh={async () => {
          await tableDetails.refresh();
        }}
        loading={loading}
        isRefreshing={isRefreshing}
        sourceType={sourceType}
        database={database}
        table={table}
        column={column}
        fields={fields}
        onClickColumn={() => onOpenField && onOpenField([])}
        onClickField={next => onOpenField && onOpenField(next)}
        onClickDataSources={onClickDataSources}
        onClickDatabases={onClickDatabases}
        onClickDatabase={onClickDatabase}
        onClickTable={onClickTable}
      />

      <div className="hue-table-browser__header-with-actions">
        <h3 className="hue-h3">{t('Type details')}</h3>
      </div>

      <div style={{ marginBottom: 16 }}>
        <MetaDataDisplay
          groups={[
            {
              items: [
                { label: t('Type path'), value: typePathLabel || t('root'), key: 'typePath' },
                {
                  label: t('Kind'),
                  value: (
                    <span className={`hue-type-label hue-type--${typeCategory}`} title={typeBase}>
                      {typeBase}
                    </span>
                  ),
                  key: 'kind'
                },
                { label: t('Raw type'), value: targetType, key: 'rawType' }
              ]
            }
          ]}
        />
      </div>

      {typeBase === 'struct' ? (
        <>
          <div className="hue-table-browser__header-with-actions">
            <h3 className="hue-h3">{t('Fields')}</h3>
            {typeBase === 'struct' && hasStructChildren && (
              <div style={{ display: 'inline-flex', gap: 8, alignItems: 'center' }}>
                <Switch checked={flattened} onChange={() => setFlattened(prev => !prev)} />
                <span>{t('Flatten nested fields')}</span>
              </div>
            )}
          </div>
          <PaginatedTable<FieldRow>
            data={rowsWithSamples}
            columns={columnsDef}
            rowKey="key"
            pagination={{
              pageStats: {
                pageNumber: 1,
                totalPages: 1,
                pageSize: Math.max(rowsWithSamples.length, 1),
                totalSize: rowsWithSamples.length
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

export default TypeDetails;
