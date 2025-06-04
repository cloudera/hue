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
import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import ImporterFilePreview from './ImporterFilePreview';
import { FileMetaData } from '../types';

const mockSave = jest.fn();
jest.mock('../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    data: {
      columns: [{ name: 'Name' }, { name: 'Age' }],
      sample: [
        ['Alice', '30'],
        ['Bob', '25']
      ]
    },
    save: mockSave,
    loading: false
  }))
}));

describe('ImporterFilePreview', () => {
  const mockFileMetaData: FileMetaData = {
    source: 'localfile',
    type: 'csv',
    path: '/path/to/file.csv'
  };

  it('should render correctly', async () => {
    render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);

    await waitFor(() => {
      expect(screen.getByText('Preview')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
      expect(screen.getByText('Finish Import')).toBeInTheDocument();
    });
  });

  it('should call guessFormat and guessFields when the component mounts', async () => {
    render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);

    await waitFor(() => {
      expect(mockSave).toHaveBeenCalledTimes(2);
    });
  });

  it('should display data in the table after previewData is available', async () => {
    render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
    });
  });
});
