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
        { name: 'hdfs', userHomeDirectory: '/user/test/hdfs' },
        { name: 'abfs', userHomeDirectory: '/user/test/abfs' },
        { name: 'ofs', userHomeDirectory: '/user/test/ozone' },
        { name: 'gs', userHomeDirectory: '/user/test/gs' }
      ],
      loading: false,
      error: null,
      reloadData: jest.fn()
    });
    // Ensure the ENABLE_DIRECT_UPLOAD is enabled
    (window as hueWindow).ENABLE_DIRECT_UPLOAD = true;
  });

  it('should render local upload and filesystem options', () => {
    render(<ImporterSourceSelector setFileMetaData={mockSetFileMetaData} />);

    expect(screen.getByText('Select a source to import from')).toBeInTheDocument();
    expect(screen.queryByText('LocalUpload')).toBeInTheDocument();
    expect(screen.getByText('Amazon S3')).toBeInTheDocument();
    expect(screen.getByText('HDFS')).toBeInTheDocument();
    expect(screen.getByText('Azure Storage')).toBeInTheDocument();
    expect(screen.getByText('Ozone')).toBeInTheDocument();
    expect(screen.getByText('Google Storage')).toBeInTheDocument();
  });

  it('should not render local upload option if ENABLE_DIRECT_UPLOAD is false', () => {
    (window as hueWindow).ENABLE_DIRECT_UPLOAD = false;
    render(<ImporterSourceSelector setFileMetaData={mockSetFileMetaData} />);

    expect(screen.getByText('Select a source to import from')).toBeInTheDocument();
    expect(screen.queryByText('LocalUpload')).not.toBeInTheDocument();
  });

  it('should open FileChooserModal when filesystem button is clicked', () => {
    (FileChooserModal as jest.Mock).mockImplementation(({ showModal }) => {
      return showModal ? <div data-testid="file-chooser">FileChooserModal</div> : null;
    });

    render(<ImporterSourceSelector setFileMetaData={mockSetFileMetaData} />);

    const s3Button = screen.getByRole('button', { name: /Amazon S3/i }); // second button (first is local upload)
    fireEvent.click(s3Button);

    expect(screen.getByTestId('file-chooser')).toBeInTheDocument();
  });

  it('should handle loading state', () => {
    (useLoadData as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
      reloadData: jest.fn()
    });

    render(<ImporterSourceSelector setFileMetaData={mockSetFileMetaData} />);

    expect(screen.getAllByTestId('loading-error-wrapper__spinner')).toHaveLength(2);
  });

  it('should display error message on fetch failure', () => {
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
