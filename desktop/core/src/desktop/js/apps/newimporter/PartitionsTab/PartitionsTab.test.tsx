// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import PartitionsTab from './PartitionsTab';
import { Partition } from '../types';

describe('PartitionsTab', () => {
  const mockOnPartitionsChange = jest.fn();

  const defaultPartitions: Partition[] = [];

  const partitionsWithData: Partition[] = [
    {
      id: 'partition_1',
      name: 'year',
      type: 'int',
      value: '2023'
    },
    {
      id: 'partition_2',
      name: 'month',
      type: 'string',
      value: 'january'
    }
  ];

  const defaultProps = {
    partitions: defaultPartitions,
    onPartitionsChange: mockOnPartitionsChange
  };

  beforeEach(() => {
    mockOnPartitionsChange.mockClear();
  });

  describe('Component Rendering', () => {
    it('should render add button when no partitions exist', () => {
      render(<PartitionsTab {...defaultProps} />);

      expect(screen.getByRole('button', { name: /add partitions/i })).toBeInTheDocument();
      expect(screen.queryByText('Partition 1')).not.toBeInTheDocument();
    });

    it('should render partitions when they exist', async () => {
      render(<PartitionsTab {...defaultProps} partitions={partitionsWithData} />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('year')).toBeInTheDocument();
        expect(screen.getByDisplayValue('month')).toBeInTheDocument();
        expect(screen.getByDisplayValue('2023')).toBeInTheDocument();
        expect(screen.getByDisplayValue('january')).toBeInTheDocument();
      });
    });

    it('should render delete buttons for each partition', async () => {
      render(<PartitionsTab {...defaultProps} partitions={partitionsWithData} />);

      const deleteButtons = screen.getAllByRole('button', { name: 'minus-circle' });

      await waitFor(() => {
        expect(deleteButtons).toHaveLength(2);
      });
    });
  });

  describe('Adding Partitions', () => {
    it('should call onPartitionsChange when adding a partition', async () => {
      const user = userEvent.setup();
      render(<PartitionsTab {...defaultProps} />);

      const addButton = screen.getByRole('button', { name: /add partitions/i });
      await user.click(addButton);

      await waitFor(() => {
        expect(mockOnPartitionsChange).toHaveBeenCalledWith([
          expect.objectContaining({
            id: expect.stringMatching(/^partition_\d+$/),
            name: '',
            type: 'string',
            value: ''
          })
        ]);
      });
    });

    it('should add new partition to existing ones', async () => {
      const user = userEvent.setup();
      render(<PartitionsTab {...defaultProps} partitions={partitionsWithData} />);

      const addButton = screen.getByRole('button', { name: /add partitions/i });
      await user.click(addButton);

      await waitFor(() => {
        expect(mockOnPartitionsChange).toHaveBeenCalledWith([
          ...partitionsWithData,
          expect.objectContaining({
            id: expect.stringMatching(/^partition_\d+$/),
            name: '',
            type: 'string',
            value: ''
          })
        ]);
      });
    });
  });

  describe('Removing Partitions', () => {
    it('should call onPartitionsChange when removing a partition', async () => {
      const user = userEvent.setup();
      render(<PartitionsTab {...defaultProps} partitions={partitionsWithData} />);

      const deleteButtons = screen.getAllByRole('button', { name: 'minus-circle' });
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(mockOnPartitionsChange).toHaveBeenCalledWith([partitionsWithData[1]]);
      });
    });

    it('should remove correct partition when multiple exist', async () => {
      const user = userEvent.setup();
      render(<PartitionsTab {...defaultProps} partitions={partitionsWithData} />);

      const deleteButtons = screen.getAllByRole('button', { name: 'minus-circle' });
      await user.click(deleteButtons[1]);

      await waitFor(() => {
        expect(mockOnPartitionsChange).toHaveBeenCalledWith([partitionsWithData[0]]);
      });
    });
  });

  describe('Editing Partition Fields', () => {
    it('should call onPartitionsChange when partition name changes', async () => {
      const user = userEvent.setup();
      render(<PartitionsTab {...defaultProps} partitions={partitionsWithData} />);

      const nameInput = screen.getByDisplayValue('year');
      await user.clear(nameInput);
      await user.type(nameInput, 'x');

      await waitFor(() => {
        expect(mockOnPartitionsChange).toHaveBeenCalled();
      });

      const lastCall =
        mockOnPartitionsChange.mock.calls[mockOnPartitionsChange.mock.calls.length - 1];

      expect(Array.isArray(lastCall[0])).toBe(true);
    });

    it('should call onPartitionsChange when partition value changes', async () => {
      const user = userEvent.setup();
      render(<PartitionsTab {...defaultProps} partitions={partitionsWithData} />);

      const valueInput = screen.getByDisplayValue('2023');
      await user.clear(valueInput);
      await user.type(valueInput, '1');

      await waitFor(() => {
        expect(mockOnPartitionsChange).toHaveBeenCalled();
      });

      const lastCall =
        mockOnPartitionsChange.mock.calls[mockOnPartitionsChange.mock.calls.length - 1];
      expect(Array.isArray(lastCall[0])).toBe(true);
    });

    it('should call onPartitionsChange when partition type changes', async () => {
      const user = userEvent.setup();
      render(<PartitionsTab {...defaultProps} partitions={partitionsWithData} />);

      const typeSelects = screen.getAllByRole('combobox');
      const firstTypeSelect = typeSelects[0];

      await user.click(firstTypeSelect);
      const bigintOption = screen.getByText('Big Integer');
      await user.click(bigintOption);

      await waitFor(() => {
        expect(mockOnPartitionsChange).toHaveBeenCalledWith([
          {
            ...partitionsWithData[0],
            type: 'bigint'
          },
          partitionsWithData[1]
        ]);
      });
    });
  });
});
