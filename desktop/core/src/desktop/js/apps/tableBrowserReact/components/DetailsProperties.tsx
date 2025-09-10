// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { useState } from 'react';
import { Card } from 'antd';
import Filter from 'cuix/dist/components/Filter';
import PaginatedTable, {
  type ColumnProps as PaginatedColumnProps
} from '../../../reactComponents/PaginatedTable/PaginatedTable';
import type { FilterOutput } from 'cuix/dist/components/Filter/types';
import { i18nReact } from '../../../utils/i18nReact';

export interface PropertyRow {
  name: string;
  value: string;
}

export interface DetailsPropertiesProps {
  // Fallback simple list
  properties?: PropertyRow[];
  // Structured sections for full details tab
  baseInfo?: PropertyRow[];
  tableParameters?: PropertyRow[];
  storageInfo?: PropertyRow[];
  storageDescParams?: PropertyRow[];
}

const DetailsProperties = ({
  properties,
  baseInfo,
  tableParameters,
  storageInfo,
  storageDescParams
}: DetailsPropertiesProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [filter, setFilter] = useState('');
  const [pageNumber, setPageNumber] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [tpPage, setTpPage] = useState(1);
  const [tpSize, setTpSize] = useState(25);
  const [siPage, setSiPage] = useState(1);
  const [siSize, setSiSize] = useState(25);
  const [sdpPage, setSdpPage] = useState(1);
  const [sdpSize, setSdpSize] = useState(25);

  const filterList = (list: PropertyRow[] | undefined): PropertyRow[] => {
    if (!list) {
      return [];
    }
    if (!filter) {
      return list;
    }
    const q = filter.toLowerCase();
    return list.filter(
      p => p.name.toLowerCase().includes(q) || (p.value || '').toLowerCase().includes(q)
    );
  };

  const filteredProps = filterList(properties);
  const filteredBase = filterList(baseInfo);
  const filteredTableParams = filterList(tableParameters);
  const filteredStorageInfo = filterList(storageInfo);
  const filteredStorageParams = filterList(storageDescParams);

  const data = filteredProps.map(p => ({ key: p.name, ...p }));
  const totalSize = data.length;
  const totalPages = Math.max(Math.ceil(totalSize / pageSize), 1);
  const start = (pageNumber - 1) * pageSize;
  const pageData = data.slice(start, start + pageSize);

  const baseData = filteredBase.map(p => ({ key: p.name, ...p }));
  const baseTotal = baseData.length;
  const baseTotalPages = Math.max(Math.ceil(baseTotal / pageSize), 1);
  const baseStart = (pageNumber - 1) * pageSize;
  const basePage = baseData.slice(baseStart, baseStart + pageSize);

  const tpData = filteredTableParams.map(p => ({ key: p.name, ...p }));
  const tpTotal = tpData.length;
  const tpTotalPages = Math.max(Math.ceil(tpTotal / tpSize), 1);
  const tpStart = (tpPage - 1) * tpSize;
  const tpPageData = tpData.slice(tpStart, tpStart + tpSize);

  const siData = filteredStorageInfo.map(p => ({ key: p.name, ...p }));
  const siTotal = siData.length;
  const siTotalPages = Math.max(Math.ceil(siTotal / siSize), 1);
  const siStart = (siPage - 1) * siSize;
  const siPageData = siData.slice(siStart, siStart + siSize);

  const sdpData = filteredStorageParams.map(p => ({ key: p.name, ...p }));
  const sdpTotal = sdpData.length;
  const sdpTotalPages = Math.max(Math.ceil(sdpTotal / sdpSize), 1);
  const sdpStart = (sdpPage - 1) * sdpSize;
  const sdpPageData = sdpData.slice(sdpStart, sdpStart + sdpSize);

  const columns: PaginatedColumnProps<PropertyRow & { key: string }>[] = [
    { title: t('Property'), dataIndex: 'name', key: 'name' },
    { title: t('Value'), dataIndex: 'value', key: 'value' }
  ];

  const hasStructured = !!(baseInfo || tableParameters || storageInfo || storageDescParams);

  return (
    <div>
      <div className="hue-table-browser__filter">
        <Filter
          search={{ placeholder: t('Filter details') }}
          onChange={(output: FilterOutput) => {
            const searchValue = String(
              (output as unknown as { search?: unknown[] }).search?.[0] ?? ''
            );
            if (searchValue !== filter) {
              setFilter(searchValue);
              setPageNumber(1);
              setTpPage(1);
              setSiPage(1);
              setSdpPage(1);
            }
          }}
        />
      </div>

      {!hasStructured && (
        <PaginatedTable<PropertyRow & { key: string }>
          data={pageData}
          columns={columns}
          rowKey="key"
          pagination={{
            pageStats: { pageNumber, totalPages, pageSize, totalSize },
            setPageNumber,
            setPageSize
          }}
        />
      )}

      {hasStructured && (
        <div className="hue-table-browser__details-grid">
          <Card title={t('Detailed Table Information')}>
            <PaginatedTable<PropertyRow & { key: string }>
              data={basePage}
              columns={columns}
              rowKey="key"
              pagination={{
                pageStats: {
                  pageNumber,
                  totalPages: baseTotalPages,
                  pageSize,
                  totalSize: baseTotal
                },
                setPageNumber,
                setPageSize
              }}
            />
          </Card>

          {!!tpData.length && (
            <Card title={t('Table Parameters')}>
              <PaginatedTable<PropertyRow & { key: string }>
                data={tpPageData}
                columns={columns}
                rowKey="key"
                pagination={{
                  pageStats: {
                    pageNumber: tpPage,
                    totalPages: tpTotalPages,
                    pageSize: tpSize,
                    totalSize: tpTotal
                  },
                  setPageNumber: setTpPage,
                  setPageSize: setTpSize
                }}
              />
            </Card>
          )}

          {!!siData.length && (
            <Card title={t('Storage Information')}>
              <PaginatedTable<PropertyRow & { key: string }>
                data={siPageData}
                columns={columns}
                rowKey="key"
                pagination={{
                  pageStats: {
                    pageNumber: siPage,
                    totalPages: siTotalPages,
                    pageSize: siSize,
                    totalSize: siTotal
                  },
                  setPageNumber: setSiPage,
                  setPageSize: setSiSize
                }}
              />
            </Card>
          )}

          {!!sdpData.length && (
            <Card title={t('Storage Desc Params')}>
              <PaginatedTable<PropertyRow & { key: string }>
                data={sdpPageData}
                columns={columns}
                rowKey="key"
                pagination={{
                  pageStats: {
                    pageNumber: sdpPage,
                    totalPages: sdpTotalPages,
                    pageSize: sdpSize,
                    totalSize: sdpTotal
                  },
                  setPageNumber: setSdpPage,
                  setPageSize: setSdpSize
                }}
              />
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default DetailsProperties;
