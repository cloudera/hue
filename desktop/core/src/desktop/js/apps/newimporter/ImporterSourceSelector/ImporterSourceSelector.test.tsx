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
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ImporterSourceSelector from './ImporterSourceSelector';

import { hueWindow } from 'types/types';

import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import FileChooserModal from '../../storageBrowser/FileChooserModal/FileChooserModal';

jest.mock('../../../utils/hooks/useLoadData/useLoadData');
jest.mock('../../storageBrowser/FileChooserModal/FileChooserModal', () => jest.fn(() => null));
jest.mock('./LocalFileUploadOption', () => () => <div data-testid="local-upload">LocalUpload</div>);

const mockSetFileMetaData = jest.fn();

describe('ImporterSourceSelector', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useLoadData as jest.Mock).mockReturnValue({
      data: [
        { name: 's3a', userHomeDirectory: '/user/test/s3' },
        { name: 'hdfs', userHomeDirectory: '/user/test/hdfs' }
      ],
      loading: false,
      error: null,
      reloadData: jest.fn()
    });
    // Ensure the ENABLE_DIRECT_UPLOAD is enabled
    (window as hueWindow).ENABLE_DIRECT_UPLOAD = true;
  });

  test('renders local upload and filesystem options', () => {
    render(<ImporterSourceSelector setFileMetaData={mockSetFileMetaData} />);

    expect(screen.getByText('Select a source to import from')).toBeInTheDocument();
    expect(screen.getByTestId('local-upload')).toBeInTheDocument();
    expect(screen.getByText('Amazon S3')).toBeInTheDocument();
    expect(screen.getByText('Hadoop Distributed File System')).toBeInTheDocument();
  });

  test('opens FileChooserModal when filesystem button is clicked', () => {
    (FileChooserModal as jest.Mock).mockImplementation(({ showModal }) => {
      return showModal ? <div data-testid="file-chooser">FileChooserModal</div> : null;
    });

    render(<ImporterSourceSelector setFileMetaData={mockSetFileMetaData} />);

    const s3Button = screen.getAllByRole('button')[1]; // second button (first is local upload)
    fireEvent.click(s3Button);

    expect(screen.getByTestId('file-chooser')).toBeInTheDocument();
  });

  test('handles loading state', () => {
    (useLoadData as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
      reloadData: jest.fn()
    });

    render(<ImporterSourceSelector setFileMetaData={mockSetFileMetaData} />);

    expect(screen.getByText('Select a source to import from')).toBeInTheDocument();
  });

  test('displays error message on fetch failure', () => {
    const mockRetry = jest.fn();
    (useLoadData as jest.Mock).mockReturnValue({
      data: null,
      loading: false,
      error: true,
      reloadData: mockRetry
    });

    render(<ImporterSourceSelector setFileMetaData={mockSetFileMetaData} />);

    expect(screen.getByText('An error occurred while fetching the filesystem')).toBeInTheDocument();
  });
});
