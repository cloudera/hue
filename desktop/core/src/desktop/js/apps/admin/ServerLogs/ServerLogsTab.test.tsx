// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ServerLogs from './ServerLogsTab';

const mockData = jest.fn().mockReturnValue({
  logs: ['Log entry 1', 'Log entry 2'],
  hue_hostname: 'test-hostname'
});

jest.mock('../../../utils/hooks/useLoadData', () => {
  return jest.fn(() => ({
    data: mockData(),
    loading: false
  }));
});


afterEach(() => {
  jest.clearAllMocks(); 
});

describe('ServerLogs Component', () => {
  test('Render ServerLogs component with fetched logs', () => {
    render(<ServerLogs />);

      expect(screen.getByText('Log entry 1')).toBeInTheDocument();
      expect(screen.getByText('Log entry 2')).toBeInTheDocument();
  });

  test('Handles no logs found scenario', () => {
    
    jest.mock('../../../utils/hooks/useLoadData', () => {
      return jest.fn(() => ({
        data: {
          logs: [],
          hue_hostname: 'test-hostname'
        },
        loading: false
      }));
    });
  
    render(<ServerLogs />);
    expect(screen.getByText('No logs found!')).toBeInTheDocument();
  });
});
