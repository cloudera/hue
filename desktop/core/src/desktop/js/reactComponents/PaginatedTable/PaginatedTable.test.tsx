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
    align?: 'left' | 'right' | 'center';
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
                ...(typeof col.width === 'number' ? { width: col.width } : {}),
                ...(col.align ? { textAlign: col.align } : {})
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
                  ...(typeof col.width === 'number' ? { width: col.width } : {}),
                  ...(col.align ? { textAlign: col.align } : {})
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

describe('PaginatedTable numerical alignment', () => {
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

  it('detects and right-aligns plain numerical columns', () => {
    type Row = { key: string; numbers: number; text: string };
    const columns: ColumnProps<Row>[] = [
      { title: 'Numbers', dataIndex: 'numbers', key: 'numbers' },
      { title: 'Text', dataIndex: 'text', key: 'text' }
    ];
    const data: Row[] = [
      { key: '0', numbers: 123, text: 'hello' },
      { key: '1', numbers: 456.78, text: 'world' },
      { key: '2', numbers: 999, text: 'test' }
    ];

    render(<PaginatedTable<Row> data={data} columns={columns} rowKey="key" pagination={{}} />);

    // Check header alignment
    const numbersHeader = screen.getByTestId('th-numbers');
    const textHeader = screen.getByTestId('th-text');

    // Numbers column should be right-aligned
    expect(numbersHeader.style.textAlign).toBe('right');
    // Text column should not be right-aligned
    expect(textHeader.style.textAlign).not.toBe('right');

    // Check cell alignment
    const numbersCell = screen.getByTestId('td-0-numbers');
    const textCell = screen.getByTestId('td-0-text');

    expect(numbersCell.style.textAlign).toBe('right');
    expect(textCell.style.textAlign).not.toBe('right');
  });

  it('detects and right-aligns currency values', () => {
    type Row = { key: string; price: string; name: string };
    const columns: ColumnProps<Row>[] = [
      { title: 'Price', dataIndex: 'price', key: 'price' },
      { title: 'Name', dataIndex: 'name', key: 'name' }
    ];
    const data: Row[] = [
      { key: '0', price: '$100,000', name: 'Product A' },
      { key: '1', price: '$25.99', name: 'Product B' },
      { key: '2', price: '$1,234.56', name: 'Product C' }
    ];

    render(<PaginatedTable<Row> data={data} columns={columns} rowKey="key" pagination={{}} />);

    const priceHeader = screen.getByTestId('th-price');
    const nameHeader = screen.getByTestId('th-name');

    expect(priceHeader.style.textAlign).toBe('right');
    expect(nameHeader.style.textAlign).not.toBe('right');
  });

  it('detects and right-aligns data sizes with units', () => {
    type Row = { key: string; size: string; filename: string };
    const columns: ColumnProps<Row>[] = [
      { title: 'Size', dataIndex: 'size', key: 'size' },
      { title: 'Filename', dataIndex: 'filename', key: 'filename' }
    ];
    const data: Row[] = [
      { key: '0', size: '500 GB', filename: 'data.csv' },
      { key: '1', size: '2.5 TB', filename: 'backup.zip' },
      { key: '2', size: '128 MB', filename: 'image.jpg' },
      { key: '3', size: '1.2 KB', filename: 'config.txt' }
    ];

    render(<PaginatedTable<Row> data={data} columns={columns} rowKey="key" pagination={{}} />);

    const sizeHeader = screen.getByTestId('th-size');
    const filenameHeader = screen.getByTestId('th-filename');

    expect(sizeHeader.style.textAlign).toBe('right');
    expect(filenameHeader.style.textAlign).not.toBe('right');
  });

  it('detects and right-aligns percentage values', () => {
    type Row = { key: string; completion: string; task: string };
    const columns: ColumnProps<Row>[] = [
      { title: 'Completion', dataIndex: 'completion', key: 'completion' },
      { title: 'Task', dataIndex: 'task', key: 'task' }
    ];
    const data: Row[] = [
      { key: '0', completion: '75%', task: 'Task A' },
      { key: '1', completion: '100%', task: 'Task B' },
      { key: '2', completion: '12.5%', task: 'Task C' }
    ];

    render(<PaginatedTable<Row> data={data} columns={columns} rowKey="key" pagination={{}} />);

    const completionHeader = screen.getByTestId('th-completion');
    const taskHeader = screen.getByTestId('th-task');

    expect(completionHeader.style.textAlign).toBe('right');
    expect(taskHeader.style.textAlign).not.toBe('right');
  });

  it('handles mixed numerical and text data correctly', () => {
    type Row = { key: string; mixed: string | number };
    const columns: ColumnProps<Row>[] = [{ title: 'Mixed', dataIndex: 'mixed', key: 'mixed' }];

    // 60% numerical (3 out of 5), should not be right-aligned (below 70% threshold)
    const mixedData: Row[] = [
      { key: '0', mixed: 123 },
      { key: '1', mixed: 'text' },
      { key: '2', mixed: 456 },
      { key: '3', mixed: 'more text' },
      { key: '4', mixed: 789 }
    ];

    render(<PaginatedTable<Row> data={mixedData} columns={columns} rowKey="key" pagination={{}} />);

    const mixedHeader = screen.getByTestId('th-mixed');
    expect(mixedHeader.style.textAlign).not.toBe('right');
  });

  it('handles predominantly numerical mixed data', () => {
    type Row = { key: string; mostlyNumbers: string | number };
    const columns: ColumnProps<Row>[] = [
      { title: 'Mostly Numbers', dataIndex: 'mostlyNumbers', key: 'mostlyNumbers' }
    ];

    // 80% numerical (4 out of 5), should be right-aligned (above 70% threshold)
    const mostlyNumericalData: Row[] = [
      { key: '0', mostlyNumbers: 123 },
      { key: '1', mostlyNumbers: 'text' },
      { key: '2', mostlyNumbers: 456 },
      { key: '3', mostlyNumbers: 789 },
      { key: '4', mostlyNumbers: 101112 }
    ];

    render(
      <PaginatedTable<Row>
        data={mostlyNumericalData}
        columns={columns}
        rowKey="key"
        pagination={{}}
      />
    );

    const mostlyNumbersHeader = screen.getByTestId('th-mostlyNumbers');
    expect(mostlyNumbersHeader.style.textAlign).toBe('right');
  });

  it('handles empty data gracefully', () => {
    type Row = { key: string; value: string };
    const columns: ColumnProps<Row>[] = [{ title: 'Value', dataIndex: 'value', key: 'value' }];
    const emptyData: Row[] = [];

    render(<PaginatedTable<Row> data={emptyData} columns={columns} rowKey="key" pagination={{}} />);

    const header = screen.getByTestId('th-value');
    // Should not crash and should not be right-aligned
    expect(header.style.textAlign).not.toBe('right');
  });

  it('handles null and undefined values in numerical detection', () => {
    type Row = { key: string; nullable: number | null | undefined };
    const columns: ColumnProps<Row>[] = [
      { title: 'Nullable', dataIndex: 'nullable', key: 'nullable' }
    ];
    const dataWithNulls: Row[] = [
      { key: '0', nullable: 123 },
      { key: '1', nullable: null },
      { key: '2', nullable: undefined },
      { key: '3', nullable: 456 },
      { key: '4', nullable: 789 }
    ];

    render(
      <PaginatedTable<Row> data={dataWithNulls} columns={columns} rowKey="key" pagination={{}} />
    );

    const header = screen.getByTestId('th-nullable');
    // Should be right-aligned because 100% of non-null values are numerical
    expect(header.style.textAlign).toBe('right');
  });

  it('preserves existing column alignment for non-numerical columns', () => {
    type Row = { key: string; leftText: string; centerText: string; rightText: string };
    const columns: ColumnProps<Row>[] = [
      { title: 'Left', dataIndex: 'leftText', key: 'leftText', align: 'left' },
      { title: 'Center', dataIndex: 'centerText', key: 'centerText', align: 'center' },
      { title: 'Right', dataIndex: 'rightText', key: 'rightText', align: 'right' }
    ];
    const data: Row[] = [{ key: '0', leftText: 'text', centerText: 'text', rightText: 'text' }];

    render(<PaginatedTable<Row> data={data} columns={columns} rowKey="key" pagination={{}} />);

    // Original alignment should be preserved for non-numerical columns
    const leftHeader = screen.getByTestId('th-leftText');
    const centerHeader = screen.getByTestId('th-centerText');
    const rightHeader = screen.getByTestId('th-rightText');

    expect(leftHeader.style.textAlign).toBe('left');
    expect(centerHeader.style.textAlign).toBe('center');
    expect(rightHeader.style.textAlign).toBe('right');
  });

  it('works correctly with horizontal scroll enabled', () => {
    type Row = { key: string; numbers: number; text: string };
    const columns: ColumnProps<Row>[] = [
      { title: 'Numbers', dataIndex: 'numbers', key: 'numbers' },
      { title: 'Text', dataIndex: 'text', key: 'text' }
    ];
    const data: Row[] = [
      { key: '0', numbers: 123, text: 'hello' },
      { key: '1', numbers: 456, text: 'world' }
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

    const numbersHeader = screen.getByTestId('th-numbers');
    const numbersCell = screen.getByTestId('td-0-numbers');
    const textHeader = screen.getByTestId('th-text');
    const textCell = screen.getByTestId('td-0-text');

    // Both header and cell should be right-aligned for numerical column
    expect(numbersHeader.style.textAlign).toBe('right');
    expect(numbersCell.style.textAlign).toBe('right');

    // Text column should not be right-aligned
    expect(textHeader.style.textAlign).not.toBe('right');
    expect(textCell.style.textAlign).not.toBe('right');
  });
});

describe('PaginatedTable memoization', () => {
  it('should memoize column processing', () => {
    type Row = { key: string; value: number };
    const columns: ColumnProps<Row>[] = [{ title: 'Value', dataIndex: 'value', key: 'value' }];
    const data: Row[] = [
      { key: '0', value: 123 },
      { key: '1', value: 456 }
    ];

    const { rerender } = render(
      <PaginatedTable<Row> data={data} columns={columns} rowKey="key" pagination={{}} />
    );

    const initialHeader = screen.getByTestId('th-value');
    expect(initialHeader.style.textAlign).toBe('right');

    // Rerender with same props - should use memoized result
    rerender(<PaginatedTable<Row> data={data} columns={columns} rowKey="key" pagination={{}} />);

    const rerenderedHeader = screen.getByTestId('th-value');
    expect(rerenderedHeader.style.textAlign).toBe('right');
  });

  it('should recalculate when data changes', () => {
    type Row = { key: string; value: string | number };
    const columns: ColumnProps<Row>[] = [{ title: 'Value', dataIndex: 'value', key: 'value' }];

    // Initially text data
    const textData: Row[] = [
      { key: '0', value: 'hello' },
      { key: '1', value: 'world' }
    ];

    const { rerender } = render(
      <PaginatedTable<Row> data={textData} columns={columns} rowKey="key" pagination={{}} />
    );

    const textHeader = screen.getByTestId('th-value');
    expect(textHeader.style.textAlign).not.toBe('right');

    // Change to numerical data
    const numericalData: Row[] = [
      { key: '0', value: 123 },
      { key: '1', value: 456 }
    ];

    rerender(
      <PaginatedTable<Row> data={numericalData} columns={columns} rowKey="key" pagination={{}} />
    );

    const numericalHeader = screen.getByTestId('th-value');
    expect(numericalHeader.style.textAlign).toBe('right');
  });

  it('should recalculate when columns change', () => {
    type Row = { key: string; value: number };
    const data: Row[] = [
      { key: '0', value: 123 },
      { key: '1', value: 456 }
    ];

    const columns1: ColumnProps<Row>[] = [{ title: 'Value', dataIndex: 'value', key: 'value' }];

    const { rerender } = render(
      <PaginatedTable<Row> data={data} columns={columns1} rowKey="key" pagination={{}} />
    );

    expect(screen.getByTestId('th-value')).toBeInTheDocument();

    // Change column configuration
    const columns2: ColumnProps<Row>[] = [
      { title: 'Different Title', dataIndex: 'value', key: 'value', align: 'center' }
    ];

    rerender(<PaginatedTable<Row> data={data} columns={columns2} rowKey="key" pagination={{}} />);

    const changedHeader = screen.getByTestId('th-value');
    expect(changedHeader).toHaveTextContent('Different Title');
    // Should still be right-aligned for numerical data, overriding the center alignment
    expect(changedHeader.style.textAlign).toBe('right');
  });
});
