import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TablesList from './TablesList';

jest.mock('cuix/dist/components/Filter', () => ({
  __esModule: true,
  default: ({ onChange }: { onChange: (output: unknown) => void }) => (
    <input aria-label="filter" onChange={e => onChange({ search: [e.currentTarget.value] })} />
  )
}));

jest.mock('cuix/dist/components/Loading', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

jest.mock('cuix/dist/components/EmptyState', () => ({
  __esModule: true,
  default: ({ title }: { title: string }) => <div>{title}</div>
}));

jest.mock('../../../reactComponents/PaginatedTable/PaginatedTable', () => ({
  __esModule: true,
  default: ({ data }: { data: { key: string; name: string }[] }) => (
    <div data-testid="rows">{data.map(r => r.name).join(',')}</div>
  )
}));

it('does not loop on same filter value', async () => {
  const setTableFilter = jest.fn();
  render(
    <TablesList
      tables={[{ name: 't1', type: 'table', comment: '' }]}
      loading={false}
      isRefreshing={false}
      tableFilter=""
      setTableFilter={setTableFilter}
      tablePageNumber={1}
      setTablePageNumber={() => {}}
      tablePageSize={50}
      setTablePageSize={() => {}}
      tableDescriptions={{}}
      editingTableName={null}
      editingTableValue=""
      setEditingTableName={() => {}}
      setEditingTableValue={() => {}}
      onOpenTable={() => {}}
      onSaveDescription={() => {}}
    />
  );

  const input = screen.getByLabelText('filter');
  await userEvent.type(input, 't');
  await userEvent.type(input, 't');

  expect(setTableFilter).toHaveBeenCalledTimes(1);
  expect(setTableFilter).toHaveBeenCalledWith('t');
});
