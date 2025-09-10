import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DatabasesList from './DatabasesList';

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
  const setDbFilter = jest.fn();
  render(
    <DatabasesList
      databases={["db1","db2"]}
      loading={false}
      isRefreshing={false}
      dbFilter=""
      setDbFilter={setDbFilter}
      dbPageNumber={1}
      setDbPageNumber={() => {}}
      dbPageSize={50}
      setDbPageSize={() => {}}
      dbDescriptions={{}}
      editingDb={null}
      editingValue=""
      setEditingDb={() => {}}
      setEditingValue={() => {}}
      onOpenDatabase={() => {}}
      onSaveDescription={() => {}}
    />
  );

  const input = screen.getByLabelText('filter');
  await userEvent.type(input, 'd');
  await userEvent.type(input, 'd');

  // first 'd' triggers setDbFilter("d"), second identical value should be ignored
  expect(setDbFilter).toHaveBeenCalledTimes(1);
  expect(setDbFilter).toHaveBeenCalledWith('d');
});
