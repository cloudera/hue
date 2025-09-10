import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SourcesList from './SourcesList';

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
  const setSourceFilter = jest.fn();
  render(
    <SourcesList
      sources={["impala","hive"]}
      loading={false}
      isRefreshing={false}
      sourceFilter=""
      setSourceFilter={setSourceFilter}
      sourcePageNumber={1}
      setSourcePageNumber={() => {}}
      sourcePageSize={50}
      setSourcePageSize={() => {}}
      onOpenSource={() => {}}
    />
  );

  const input = screen.getByLabelText('filter');
  await userEvent.type(input, 'i');
  await userEvent.type(input, 'i');

  expect(setSourceFilter).toHaveBeenCalledTimes(1);
  expect(setSourceFilter).toHaveBeenCalledWith('i');
});
