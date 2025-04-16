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
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskLogsModal from './TaskLogsModal';
import { TaskServerResponse } from '../types';

jest.mock('../../../utils/hooks/useLoadData/useLoadData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    data: 'Sample log data',
    loading: false,
    error: null
  }))
}));

describe('TaskLogsModal', () => {
  const mockOnClose = jest.fn();
  const taskId: TaskServerResponse['taskId'] = '123';

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders the modal with task logs', () => {
    render(<TaskLogsModal taskId={taskId} onClose={mockOnClose} />);

    expect(screen.getByText('Task Logs')).toBeInTheDocument();
    expect(screen.getByText('Sample log data')).toBeInTheDocument();
  });
});
