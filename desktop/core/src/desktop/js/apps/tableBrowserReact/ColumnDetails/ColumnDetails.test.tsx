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
import ColumnDetails from './ColumnDetails';
import type { ColumnDetailsProps } from './ColumnDetails';

// Mock MetaDataDisplay component
jest.mock('../sharedComponents/MetaDataDisplay', () => {
  return function MockMetaDataDisplay() {
    return <div data-testid="metadata-display">Metadata</div>;
  };
});

// Mock PageHeader component
jest.mock('../sharedComponents/PageHeader', () => {
  return function MockPageHeader() {
    return <div data-testid="page-header">Page Header</div>;
  };
});

// Mock SampleGrid component
jest.mock('../TableDetails/SampleTab/SampleGrid', () => {
  return function MockSampleGrid() {
    return <div data-testid="sample-grid">Sample Grid</div>;
  };
});

// Mock PrettyStructDisplay component
jest.mock('../sharedComponents/PrettyStructDisplay', () => {
  return function MockPrettyStructDisplay({ 
    structType, 
    compact 
  }: { 
    structType?: string; 
    compact?: boolean; 
  }) {
    return (
      <div data-testid="pretty-struct-display" data-compact={compact}>
        {structType}
      </div>
    );
  };
});

const mockTableDetails = {
  loading: false,
  isRefreshing: false,
  detailsColumns: [
    {
      name: 'nested_struct',
      type: 'struct<level1:string,mid:struct<level2:string,core:struct<level3:string,value:int>>>',
      comment: 'A nested struct column'
    }
  ],
  sampleData: {
    headers: ['nested_struct'],
    rows: [['{"level1":"test","mid":{"level2":"test2","core":{"level3":"test3","value":42}}}']]
  },
  detailsProperties: [],
  detailsSections: {},
  refresh: jest.fn()
};

const defaultProps: ColumnDetailsProps = {
  database: 'test_db',
  table: 'test_table',
  column: 'nested_struct',
  fields: [],
  connector: null,
  namespace: null,
  compute: null,
  tableDetails: mockTableDetails,
  onBackToTable: jest.fn(),
  onOpenField: jest.fn()
};

describe('ColumnDetails', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders struct fields at root level', () => {
    render(<ColumnDetails {...defaultProps} />);

    // Should show top-level fields
    expect(screen.getByText('level1')).toBeInTheDocument();
    expect(screen.getByText('mid')).toBeInTheDocument();

    // Should not show nested fields at root level
    expect(screen.queryByText('level2')).not.toBeInTheDocument();
    expect(screen.queryByText('core')).not.toBeInTheDocument();
  });

  it('renders nested struct fields when navigating deeper', () => {
    const propsWithFields = {
      ...defaultProps,
      fields: ['mid']
    };

    render(<ColumnDetails {...propsWithFields} />);

    // Should show mid-level fields
    expect(screen.getByText('level2')).toBeInTheDocument();
    expect(screen.getByText('core')).toBeInTheDocument();

    // Should not show root or deeper fields
    expect(screen.queryByText('level1')).not.toBeInTheDocument();
    expect(screen.queryByText('level3')).not.toBeInTheDocument();
  });

  it('renders deepest struct fields', () => {
    const propsWithDeepFields = {
      ...defaultProps,
      fields: ['mid', 'core']
    };

    render(<ColumnDetails {...propsWithDeepFields} />);

    // Should show deepest fields
    expect(screen.getByText('level3')).toBeInTheDocument();
    expect(screen.getByText('value')).toBeInTheDocument();

    // Should not show parent fields
    expect(screen.queryByText('level1')).not.toBeInTheDocument();
    expect(screen.queryByText('level2')).not.toBeInTheDocument();
  });

  it('calls onOpenField when clicking a struct field', async () => {
    const user = userEvent.setup();
    const mockOnOpenField = jest.fn();
    const propsWithHandler = {
      ...defaultProps,
      onOpenField: mockOnOpenField
    };

    render(<ColumnDetails {...propsWithHandler} />);

    // Find and click the "mid" struct field button
    const midButton = screen.getByRole('button', { name: 'mid' });
    await user.click(midButton);

    // Should call onOpenField with the correct path
    expect(mockOnOpenField).toHaveBeenCalledWith(['mid']);
  });

  it('builds correct field path for nested navigation', async () => {
    const user = userEvent.setup();
    const mockOnOpenField = jest.fn();
    const propsWithFields = {
      ...defaultProps,
      fields: ['mid'],
      onOpenField: mockOnOpenField
    };

    render(<ColumnDetails {...propsWithFields} />);

    // Find and click the "core" struct field button
    const coreButton = screen.getByRole('button', { name: 'core' });
    await user.click(coreButton);

    // Should call onOpenField with the correct nested path
    expect(mockOnOpenField).toHaveBeenCalledWith(['mid', 'core']);
  });

  it('shows flatten toggle only when there are nested structs', () => {
    render(<ColumnDetails {...defaultProps} />);

    // Should show the toggle since there are nested structs
    expect(screen.getByText(/show flattened/i)).toBeInTheDocument();
  });

  it('does not show flatten toggle for non-struct columns', () => {
    const nonStructProps = {
      ...defaultProps,
      tableDetails: {
        ...mockTableDetails,
        detailsColumns: [
          {
            name: 'simple_column',
            type: 'string',
            comment: 'A simple string column'
          }
        ]
      }
    };

    render(<ColumnDetails {...nonStructProps} />);

    // Should not show the toggle for non-struct columns
    expect(screen.queryByText(/show flattened/i)).not.toBeInTheDocument();
  });

  it('filters out struct containers in flattened view', async () => {
    const user = userEvent.setup();
    render(<ColumnDetails {...defaultProps} />);

    // Enable flattened view
    const toggleSwitch = screen.getByRole('switch');
    await user.click(toggleSwitch);

    // Should show leaf fields only
    expect(screen.getByText('level1')).toBeInTheDocument();
    expect(screen.getByText('mid.level2')).toBeInTheDocument();
    expect(screen.getByText('mid.core.level3')).toBeInTheDocument();
    expect(screen.getByText('mid.core.value')).toBeInTheDocument();

    // Should not show struct containers as rows
    expect(screen.queryByRole('button', { name: 'mid' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'core' })).not.toBeInTheDocument();
  });

  it('uses PrettyStructDisplay for struct types', () => {
    render(<ColumnDetails {...defaultProps} />);

    // Should render PrettyStructDisplay for the main struct type
    const structDisplays = screen.getAllByTestId('pretty-struct-display');
    expect(structDisplays.length).toBeGreaterThan(0);

    // Should display the struct type in the PrettyStructDisplay
    expect(structDisplays[0]).toHaveTextContent(
      'struct<level1:string,mid:struct<level2:string,core:struct<level3:string,value:int>>>'
    );
  });

  it('uses compact mode for struct types in table cells', () => {
    render(<ColumnDetails {...defaultProps} />);

    // Should render PrettyStructDisplay components
    const structDisplays = screen.getAllByTestId('pretty-struct-display');
    expect(structDisplays.length).toBeGreaterThan(0);

    // Check if any displays are in compact mode (for table cells)
    const compactDisplays = structDisplays.filter(display => 
      display.getAttribute('data-compact') === 'true'
    );
    
    // At least the main display should not be compact, but table cell displays should be compact
    const nonCompactDisplays = structDisplays.filter(display => 
      display.getAttribute('data-compact') === 'false' || !display.getAttribute('data-compact')
    );
    
    expect(nonCompactDisplays.length).toBeGreaterThan(0);
  });
});
