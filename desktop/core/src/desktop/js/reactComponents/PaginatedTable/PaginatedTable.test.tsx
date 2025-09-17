// Licensed to Cloudera, Inc. under one
// or more contributor license agreements. See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock CUIX Table with a minimal implementation that applies column widths
jest.mock('cuix/dist/components/Table', () => {
  interface MockColumn {
    key?: string;
    dataIndex?: string;
    title?: string;
    width?: number;
    onHeaderCell?: (col: unknown) => { style?: React.CSSProperties };
    onCell?: (row: Record<string, unknown>, index: number) => { style?: React.CSSProperties };
  }

  const MockTable = ({
    columns,
    dataSource
  }: {
    columns: MockColumn[];
    dataSource: Record<string, unknown>[];
  }) => {
    return (
      <table data-testid="mock-table">
        <thead>
          <tr>
            {columns.map((col: MockColumn, idx: number) => {
              const headerProps = col.onHeaderCell ? col.onHeaderCell(col) : {};
              const style = {
                ...(headerProps.style || {}),
                ...(typeof col.width === 'number' ? { width: col.width } : {})
              } as React.CSSProperties;
              const key = String(col.key ?? col.dataIndex ?? idx);
              return (
                <th key={key} data-testid={`th-${key}`} style={style}>
                  {col.title ?? col.dataIndex}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {dataSource.map((row: Record<string, unknown>, rowIndex: number) => (
            <tr key={String(row.key ?? rowIndex)}>
              {columns.map((col: MockColumn, colIndex: number) => {
                const cellProps = col.onCell ? col.onCell(row, rowIndex) : {};
                const style = {
                  ...(cellProps.style || {}),
                  ...(typeof col.width === 'number' ? { width: col.width } : {})
                } as React.CSSProperties;
                const key = String(col.key ?? col.dataIndex ?? colIndex);
                const value = row[(col.dataIndex as string) || ''] as unknown as string;
                return (
                  <td
                    key={`${rowIndex}-${key}`}
                    data-testid={`td-${rowIndex}-${key}`}
                    style={style}
                  >
                    {String(value ?? '')}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };
  return { __esModule: true, default: MockTable };
});

import PaginatedTable, { type ColumnProps } from './PaginatedTable';

// Helper to parse numeric pixel width from inline style
const getWidthPx = (el: HTMLElement): number => {
  const w = el.style.width || el.style.minWidth || el.style.maxWidth;
  return w ? parseInt(w, 10) : 0;
};

describe('PaginatedTable horizontal sizing', () => {
  beforeEach(() => {
    // Mock canvas measureText to a deterministic function
    const origGetContext = HTMLCanvasElement.prototype.getContext as unknown as (
      contextId: string
    ) => CanvasRenderingContext2D | null;
    (window as unknown as { __origGetContext?: unknown }).__origGetContext = origGetContext;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (HTMLCanvasElement.prototype.getContext as any) = () => ({
      measureText: (text: string) => ({ width: text.length * 10 })
    });
  });

  afterEach(() => {
    const saved = (window as unknown as { __origGetContext?: unknown }).__origGetContext as
      | typeof HTMLCanvasElement.prototype.getContext
      | undefined;
    if (saved) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (HTMLCanvasElement.prototype.getContext as any) = saved as unknown;
    }
  });

  it('expands to fit long header even if values are short', () => {
    type Row = { key: string; col: string };
    const columns: ColumnProps<Row>[] = [
      { title: 'Very Long Column Header Name', dataIndex: 'col', key: 'col' }
    ];
    const data: Row[] = [
      { key: '0', col: 'val' },
      { key: '1', col: 'val2' }
    ];

    render(
      <PaginatedTable<Row>
        data={data}
        columns={columns}
        rowKey="key"
        enableHorizontalScroll
        pagination={{}}
      />
    );

    const th = screen.getByTestId('th-col');
    const td = screen.getByTestId('td-0-col');
    const thWidth = getWidthPx(th);
    const tdWidth = getWidthPx(td);

    expect(thWidth).toBeGreaterThan(0);
    expect(tdWidth).toBeGreaterThanOrEqual(thWidth);
  });

  it('expands to fit long values even if header is short', () => {
    type Row = { key: string; col: string };
    const columns: ColumnProps<Row>[] = [{ title: 'Col', dataIndex: 'col', key: 'col' }];
    const data: Row[] = [
      { key: '0', col: 'a'.repeat(50) },
      { key: '1', col: 'b' }
    ];

    render(
      <PaginatedTable<Row>
        data={data}
        columns={columns}
        rowKey="key"
        enableHorizontalScroll
        pagination={{}}
      />
    );

    const th = screen.getByTestId('th-col');
    const td = screen.getByTestId('td-0-col');
    const thWidth = getWidthPx(th);
    const tdWidth = getWidthPx(td);

    expect(tdWidth).toBeGreaterThanOrEqual(thWidth);
    expect(tdWidth).toBeGreaterThan(0);
  });

  it('handles multiple columns with mixed long header/value', () => {
    type Row = { key: string; a: string; b: string };
    const columns: ColumnProps<Row>[] = [
      { title: 'Very Very Long Header For Column A', dataIndex: 'a', key: 'a' },
      { title: 'B', dataIndex: 'b', key: 'b' }
    ];
    const data: Row[] = [{ key: '0', a: 'x', b: 'y'.repeat(60) }];

    render(
      <PaginatedTable<Row>
        data={data}
        columns={columns}
        rowKey="key"
        enableHorizontalScroll
        pagination={{}}
      />
    );

    const thA = screen.getByTestId('th-a');
    const tdA = screen.getByTestId('td-0-a');
    const thB = screen.getByTestId('th-b');
    const tdB = screen.getByTestId('td-0-b');

    // A should size to header; B should size to long value
    expect(getWidthPx(tdA)).toBeGreaterThanOrEqual(getWidthPx(thA));
    expect(getWidthPx(tdB)).toBeGreaterThanOrEqual(getWidthPx(thB));
    expect(getWidthPx(tdB)).toBeGreaterThan(getWidthPx(tdA));
  });

  it('does not apply explicit widths when enableHorizontalScroll is false', () => {
    type Row = { key: string; col: string };
    const columns: ColumnProps<Row>[] = [
      { title: 'Very Very Long Header', dataIndex: 'col', key: 'col' }
    ];
    const data: Row[] = [{ key: '0', col: 'short' }];

    render(
      <PaginatedTable<Row>
        data={data}
        columns={columns}
        rowKey="key"
        enableHorizontalScroll={false}
        pagination={{}}
      />
    );

    const th = screen.getByTestId('th-col');
    const td = screen.getByTestId('td-0-col');
    expect(getWidthPx(th)).toBe(0);
    expect(getWidthPx(td)).toBe(0);
  });
});
