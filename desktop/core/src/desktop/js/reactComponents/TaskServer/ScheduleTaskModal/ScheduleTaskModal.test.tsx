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
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScheduleTaskModal from './ScheduleTaskModal';
import { SCHEDULE_NEW_TASK_URL, scheduleTasksCategory } from '../constants';

const mockOnClose = jest.fn();
const mockHandleSubmit = jest.fn();
const mockSaveURL = jest.fn();
jest.mock('../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(url => {
    mockSaveURL(url);
    return {
      save: mockHandleSubmit,
      loading: false,
      error: null
    };
  })
}));

describe('ScheduleTaskModal', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should render the radio group', () => {
    render(<ScheduleTaskModal onClose={mockOnClose} />);
    const radioGroup = screen.getAllByRole('radio');
    expect(radioGroup).toHaveLength(2);
    expect(radioGroup[0]).toBeInTheDocument();
    expect(radioGroup[0]).toHaveAttribute('value', scheduleTasksCategory[0].value);
    expect(radioGroup[1]).toBeInTheDocument();
    expect(radioGroup[1]).toHaveAttribute('value', scheduleTasksCategory[1].value);
  });

  it('should render one input when document_cleanup is selected', () => {
    render(<ScheduleTaskModal onClose={mockOnClose} />);
    const radioButton = screen.getByRole('radio', { name: 'Document Cleanup' });

    fireEvent.click(radioButton);

    const inputs = screen.getAllByRole('spinbutton');
    expect(inputs).toHaveLength(1);
    expect(inputs[0]).toBeInTheDocument();
    expect(inputs[0]).toHaveAttribute('name', scheduleTasksCategory[0].children[0].value);
  });

  it('should render one input when temp_cleanup is selected', async () => {
    render(<ScheduleTaskModal onClose={mockOnClose} />);
    const radioButton = screen.getByRole('radio', { name: 'Tmp Cleanup' });

    fireEvent.click(radioButton);

    const inputs = screen.getAllByRole('spinbutton');
    await waitFor(() => {
      expect(inputs).toHaveLength(2);
      expect(inputs[0]).toBeInTheDocument();
      expect(inputs[0]).toHaveAttribute('name', scheduleTasksCategory[1].children[0].value);
      expect(inputs[1]).toBeInTheDocument();
      expect(inputs[1]).toHaveAttribute('name', scheduleTasksCategory[1].children[1].value);
    });
  });

  it('should call onClose when the close button is clicked', async () => {
    render(<ScheduleTaskModal onClose={mockOnClose} />);
    const closeButton = screen.getByRole('button', { name: 'Close' });

    fireEvent.click(closeButton);

    await waitFor(() => expect(mockOnClose).toHaveBeenCalledTimes(1));
  });

  it('should trigger handleSubmit when the submit button is clicked', async () => {
    render(<ScheduleTaskModal onClose={mockOnClose} />);
    const radioButton = screen.getByRole('radio', { name: 'Document Cleanup' });

    fireEvent.click(radioButton);

    const input = screen.getByRole('spinbutton');
    fireEvent.change(input, { target: { value: '10' } });

    const submitButton = screen.getByRole('button', { name: /schedule/i });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockHandleSubmit).toHaveBeenCalledTimes(1);
      expect(mockHandleSubmit).toHaveBeenCalledWith({
        taskName: 'document_cleanup',
        taskParams: {
          keep_days: '10'
        }
      });
      expect(mockSaveURL).toHaveBeenCalledWith(SCHEDULE_NEW_TASK_URL);
    });
  });
});
