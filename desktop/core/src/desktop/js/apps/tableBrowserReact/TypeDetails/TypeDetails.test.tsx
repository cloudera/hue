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
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import TypeDetails from './TypeDetails';
import type { TableDetailsState } from '../hooks/useTableDetails';

// Mocks
jest.mock('../sharedComponents/MetaDataDisplay', () => ({
  __esModule: true,
  default: () => <div data-testid="metadata-display">Metadata</div>
}));

jest.mock('../sharedComponents/PageHeader', () => ({
  __esModule: true,
  default: () => <div data-testid="page-header">Page Header</div>
}));

jest.mock('../TableDetails/SampleTab/SampleGrid', () => ({
  __esModule: true,
  default: () => <div data-testid="sample-grid">Sample Grid</div>
}));

jest.mock('../sharedComponents/PrettyStructDisplay', () => ({
  __esModule: true,
  default: ({ structType, compact }: { structType?: string; compact?: boolean }) => (
    <div data-testid="pretty-struct-display" data-compact={compact}>
      {structType}
    </div>
  )
}));

const tableDetails: TableDetailsState = {
  loading: false,
  isRefreshing: false,
  overviewProps: undefined,
  detailsColumns: [
    {
      name: 'nested_struct',
      type: 'struct<level1:string,mid:struct<level2:string,core:struct<level3:string,value:int>>>',
      comment: 'Nested struct'
    }
  ],
  detailsProperties: [],
  detailsSections: {},
  sampleData: {
    headers: ['nested_struct'],
    rows: [['{"level1":"a","mid":{"level2":"b","core":{"level3":"c","value":1}}}']]
  },
  partitionCount: undefined,
  rawAnalysis: undefined,
  refresh: jest.fn()
};

describe('TypeDetails', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows flatten toggle when struct has nested child structs', () => {
    render(
      <TypeDetails
        database="db"
        table="tbl"
        column="nested_struct"
        fields={[]}
        tableDetails={tableDetails}
      />
    );

    expect(screen.getByText(/type details/i)).toBeInTheDocument();
    // At root, there is a nested struct child under mid.core => show toggle
    expect(screen.getByText(/flatten/i)).toBeInTheDocument();
  });

  it('navigates deeper when clicking a struct field', async () => {
    const user = userEvent.setup();
    const onOpenField = jest.fn();

    render(
      <TypeDetails
        database="db"
        table="tbl"
        column="nested_struct"
        fields={['mid']}
        tableDetails={tableDetails}
        onOpenField={onOpenField}
      />
    );

    // The direct child 'core' is a struct -> rendered as a button
    const coreBtn = screen.getByRole('button', { name: 'core' });
    await user.click(coreBtn);
    expect(onOpenField).toHaveBeenCalledWith(['mid', 'core']);
  });

  it('shows sample grid when the target type is not struct', () => {
    render(
      <TypeDetails
        database="db"
        table="tbl"
        column="nested_struct"
        fields={['mid', 'level2']}
        tableDetails={tableDetails}
      />
    );

    expect(screen.getByText(/sample values/i)).toBeInTheDocument();
    expect(screen.getByTestId('sample-grid')).toBeInTheDocument();
  });
});
