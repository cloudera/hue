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
      sources={['impala', 'hive']}
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
