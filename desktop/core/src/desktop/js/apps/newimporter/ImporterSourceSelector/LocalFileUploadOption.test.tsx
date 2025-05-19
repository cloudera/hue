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
import huePubSub from '../../../utils/huePubSub';

const mockSave = jest.fn();

jest.mock('../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave
  }))
}));

jest.mock('../../../utils/huePubSub', () => ({
  __esModule: true,
  default: {
    publish: jest.fn()
  }
}));

jest.mock('../../../utils/i18nReact', () => ({
  i18nReact: {
    useTranslation: () => ({
      t: (key: string) => key
    })
  }
}));

const mockSetFileMetaData = jest.fn();

describe('LocalFileUploadOption', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders upload button and label', () => {
    render(<LocalFileUploadOption setFileMetaData={mockSetFileMetaData} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByText('Upload from File')).toBeInTheDocument();
  });

  test('clicking the button triggers input click', () => {
    render(<LocalFileUploadOption setFileMetaData={mockSetFileMetaData} />);
    const fileInput = screen.getByTestId('hue-file-input');
    const clickSpy = jest.spyOn(fileInput, 'click');
    fireEvent.click(screen.getByRole('button'));
    expect(clickSpy).toHaveBeenCalled();
  });

  test('shows warning for empty file', () => {
    render(<LocalFileUploadOption setFileMetaData={mockSetFileMetaData} />);

    const file = new File([], 'empty.csv', { type: 'text/csv' });

    fireEvent.change(screen.getByTestId('hue-file-input'), {
      target: { files: [file] }
    });

    expect(huePubSub.publish).toHaveBeenCalledWith(
      'hue.global.warning',
      expect.objectContaining({
        message: 'This file is empty, please select another file.'
      })
    );
  });

  test('shows warning for file > 200KB', () => {
    render(<LocalFileUploadOption setFileMetaData={mockSetFileMetaData} />);

    const largeFile = new File([new ArrayBuffer(201000)], 'big.csv', { type: 'text/csv' });

    fireEvent.change(screen.getByTestId('hue-file-input'), {
      target: { files: [largeFile] }
    });

    expect(huePubSub.publish).toHaveBeenCalledWith(
      'hue.global.warning',
      expect.objectContaining({
        message: expect.stringContaining('File size exceeds')
      })
    );
  });

  test('uploads file successfully and sets metadata', () => {
    mockSave.mockImplementation((_data, { onSuccess }) => {
      onSuccess({
        local_file_url: '/tmp/foo.csv',
        file_type: 'csv'
      });
    });

    render(<LocalFileUploadOption setFileMetaData={mockSetFileMetaData} />);

    const file = new File(['dummy data'], 'data.csv', { type: 'text/csv' });

    fireEvent.change(screen.getByTestId('hue-file-input'), {
      target: { files: [file] }
    });
    expect(mockSetFileMetaData).toHaveBeenCalledWith({
      path: '/tmp/foo.csv',
      type: 'csv',
      source: ImporterFileSource.LOCAL
    });
  });

  test('handles upload error and publishes hue.error', () => {
    const error = new Error('upload failed');
    mockSave.mockImplementation((_data, { onError }) => {
      onError(error);
    });

    render(<LocalFileUploadOption setFileMetaData={mockSetFileMetaData} />);

    const file = new File(['data'], 'fail.csv', { type: 'text/csv' });

    fireEvent.change(screen.getByTestId('hue-file-input'), {
      target: { files: [file] }
    });
    expect(huePubSub.publish).toHaveBeenCalledWith('hue.error', error);
  });
});
