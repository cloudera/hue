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
import { fireEvent, render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import LocalFileUploadOption from './LocalFileUploadOption';

import { ImporterFileSource } from '../types';

const mockSave = jest.fn();

jest.mock('../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave
  }))
}));

jest.mock('../constants', () => ({
  ...jest.requireActual('../constants'),
  SUPPORTED_UPLOAD_TYPES: '.csv, .xlsx, .xls',
  DEFAULT_UPLOAD_LIMIT: 150 * 1000 * 1000
}));

const mockSetFileMetaData = jest.fn();
const mockSetUploadError = jest.fn();

describe('LocalFileUploadOption', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render upload button and label', () => {
    render(
      <LocalFileUploadOption
        setFileMetaData={mockSetFileMetaData}
        setUploadError={mockSetUploadError}
      />
    );
    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByText('Upload from File')).toBeInTheDocument();
  });

  it('should trigger input click on button click', () => {
    render(
      <LocalFileUploadOption
        setFileMetaData={mockSetFileMetaData}
        setUploadError={mockSetUploadError}
      />
    );
    const fileInput = screen.getByTestId('hue-file-input');
    const clickSpy = jest.spyOn(fileInput, 'click');
    fireEvent.click(screen.getByRole('button'));
    expect(clickSpy).toHaveBeenCalled();
  });

  it('should show warning for empty file', () => {
    render(
      <LocalFileUploadOption
        setFileMetaData={mockSetFileMetaData}
        setUploadError={mockSetUploadError}
      />
    );

    const file = new File([], 'empty.csv', { type: 'text/csv' });

    fireEvent.change(screen.getByTestId('hue-file-input'), {
      target: { files: [file] }
    });

    expect(mockSetUploadError).toHaveBeenCalledWith(
      'This file is empty, please select another file.'
    );
  });

  it('should show error for file > 150MB', () => {
    render(
      <LocalFileUploadOption
        setFileMetaData={mockSetFileMetaData}
        setUploadError={mockSetUploadError}
      />
    );

    const largeFile = new File([new ArrayBuffer(200000000)], 'big.csv', { type: 'text/csv' });

    fireEvent.change(screen.getByTestId('hue-file-input'), {
      target: { files: [largeFile] }
    });

    expect(mockSetUploadError).toHaveBeenCalledWith(
      'File size exceeds the supported size. Please use any file browser to upload files.'
    );
  });

  it('should upload file successfully and sets metadata', () => {
    mockSave.mockImplementation((_data, { onSuccess }) => {
      onSuccess({
        filePath: '/tmp/data.csv',
        fileName: 'data.csv',
        source: ImporterFileSource.LOCAL
      });
    });

    render(
      <LocalFileUploadOption
        setFileMetaData={mockSetFileMetaData}
        setUploadError={mockSetUploadError}
      />
    );

    const file = new File(['dummy data'], 'data.csv', { type: 'text/csv' });

    fireEvent.change(screen.getByTestId('hue-file-input'), {
      target: { files: [file] }
    });
    expect(mockSetFileMetaData).toHaveBeenCalledWith({
      path: '/tmp/data.csv',
      fileName: 'data.csv',
      source: ImporterFileSource.LOCAL
    });
  });

  it('should handle upload error', () => {
    const error = new Error('upload failed');
    mockSave.mockImplementation((_data, { onError }) => {
      onError(error);
    });

    render(
      <LocalFileUploadOption
        setFileMetaData={mockSetFileMetaData}
        setUploadError={mockSetUploadError}
      />
    );

    const file = new File(['data'], 'fail.csv', { type: 'text/csv' });

    fireEvent.change(screen.getByTestId('hue-file-input'), {
      target: { files: [file] }
    });
    expect(mockSetUploadError).toHaveBeenCalledWith(error.message);
  });
});
