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
import StorageFilePage from './StorageFilePage';
import { BrowserViewType, FileStats } from '../../../reactComponents/FileChooser/types';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { DOWNLOAD_API_URL } from '../../../reactComponents/FileChooser/api';
import huePubSub from '../../../utils/huePubSub';

jest.mock('../../../utils/dateTimeUtils', () => ({
  ...jest.requireActual('../../../utils/dateTimeUtils'),
  formatTimestamp: () => 'April 8, 2021 at 00:00 AM'
}));

jest.mock('../../../utils/huePubSub', () => ({
  publish: jest.fn()
}));

const mockSave = jest.fn();
jest.mock('../../../api/utils', () => ({
  post: () => mockSave()
}));

const mockData = jest.fn().mockReturnValue({
  contents: 'Initial file content',
  compression: 'none'
});

jest.mock('../../../utils/hooks/useLoadData', () => {
  return jest.fn(() => ({
    data: mockData(),
    loading: false
  }));
});

const mockConfig = {
  storage_browser: {
    enable_file_download_button: true,
    max_file_editor_size: 1000000000
  }
};
jest.mock('../../../config/hueConfig', () => ({
  getLastKnownConfig: () => mockConfig
}));

const mockFileStats: FileStats = {
  path: '/path/to/file.txt',
  size: 123456,
  user: 'testuser',
  group: 'testgroup',
  mtime: 1617877200,
  atime: 1617877200,
  mode: 33188,
  rwx: 'rwxr-xr-x',
  blockSize: 1,
  replication: 1,
  type: BrowserViewType.file
};
const mockFileName = 'file.txt';
const mockReload = jest.fn();

describe('StorageFilePage', () => {
  it('should render file metadata and content', () => {
    render(
      <StorageFilePage fileName={mockFileName} fileStats={mockFileStats} onReload={mockReload} />
    );

    expect(screen.getByText('Size')).toBeInTheDocument();
    expect(screen.getByText('120.56 KB')).toBeInTheDocument();
    expect(screen.getByText('Created By')).toBeInTheDocument();
    expect(screen.getByText('testuser')).toBeInTheDocument();
    expect(screen.getByText('Group')).toBeInTheDocument();
    expect(screen.getByText('testgroup')).toBeInTheDocument();
    expect(screen.getByText('Permissions')).toBeInTheDocument();
    expect(screen.getByText('rwxr-xr-x')).toBeInTheDocument();
    expect(screen.getByText('Last Modified')).toBeInTheDocument();
    expect(screen.getByText('April 8, 2021 at 00:00 AM')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();

    // TODO: fix this test when mocking of useLoadData onSuccess callback is mproperly mocked
    // expect(screen.getByText('Initial file content')).toBeInTheDocument();
  });

  // TODO: fix this test when mocking of useLoadData onSuccess callback is mproperly mocked
  it.skip('should show edit button and hides save/cancel buttons initially', () => {
    render(
      <StorageFilePage fileName={mockFileName} fileStats={mockFileStats} onReload={mockReload} />
    );

    expect(screen.getByRole('button', { name: 'Edit' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Save' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Cancel' })).toBeNull();
  });

  // TODO: fix this test when mocking of useLoadData onSuccess callback is mproperly mocked
  it.skip('should hide edit button when compression is available', async () => {
    mockData.mockImplementation(() => ({
      contents: 'Initial file content',
      compression: 'zip'
    }));
    render(
      <StorageFilePage fileName={mockFileName} fileStats={mockFileStats} onReload={mockReload} />
    );

    expect(screen.queryByRole('button', { name: 'Edit' })).toBeNull();
  });

  it('should show save and cancel buttons when editing', async () => {
    const user = userEvent.setup();
    render(
      <StorageFilePage fileName={mockFileName} fileStats={mockFileStats} onReload={mockReload} />
    );

    expect(screen.getByRole('button', { name: 'Edit' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Save' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Cancel' })).toBeNull();

    await user.click(screen.getByRole('button', { name: 'Edit' }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Save' })).toBeVisible();
      expect(screen.getByRole('button', { name: 'Cancel' })).toBeVisible();
    });

    expect(screen.queryByRole('button', { name: 'Edit' })).toBeNull();
  });

  it('should update textarea value and calls handleSave', async () => {
    const user = userEvent.setup();
    render(
      <StorageFilePage fileName={mockFileName} fileStats={mockFileStats} onReload={mockReload} />
    );

    await user.click(screen.getByRole('button', { name: 'Edit' }));

    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeVisible();

    await user.clear(textarea);
    await user.type(textarea, 'Updated file content');

    expect(textarea).toHaveValue('Updated file content');

    await user.click(screen.getByRole('button', { name: 'Save' }));

    expect(screen.getByText('Updated file content')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Save' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Cancel' })).toBeNull();
    expect(screen.getByRole('button', { name: 'Edit' })).toBeVisible();
  });

  it('should cancel editing and reverts textarea value', async () => {
    const user = userEvent.setup();
    render(
      <StorageFilePage fileName={mockFileName} fileStats={mockFileStats} onReload={mockReload} />
    );

    await user.click(screen.getByRole('button', { name: 'Edit' }));

    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeVisible();

    await user.clear(textarea);
    await user.type(textarea, 'Updated file content');
    expect(textarea).toHaveValue('Updated file content');

    await user.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(textarea).toHaveValue('Initial file content');
    expect(screen.queryByRole('button', { name: 'Save' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Cancel' })).toBeNull();
    expect(screen.getByRole('button', { name: 'Edit' })).toBeVisible();
  });

  it('should download a file when download button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <StorageFilePage fileName={mockFileName} fileStats={mockFileStats} onReload={mockReload} />
    );

    await user.click(screen.getByRole('button', { name: 'Download' }));

    expect(huePubSub.publish).toHaveBeenCalledWith('hue.global.info', {
      message: 'Downloading your file, Please wait...'
    });

    const downloadLink = screen.getByRole('link', { name: 'Download' });
    expect(downloadLink).toHaveAttribute('href', `${DOWNLOAD_API_URL}${mockFileStats.path}`);
  });

  it('should download a file when download button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <StorageFilePage fileName={mockFileName} fileStats={mockFileStats} onReload={mockReload} />
    );

    await user.click(screen.getByRole('button', { name: 'Download' }));

    expect(huePubSub.publish).toHaveBeenCalledWith('hue.global.info', {
      message: 'Downloading your file, Please wait...'
    });

    const downloadLink = screen.getByRole('link', { name: 'Download' });
    expect(downloadLink).toHaveAttribute('href', `${DOWNLOAD_API_URL}${mockFileStats.path}`);
  });

  it('should not render the download button when show_download_button is false', () => {
    mockConfig.storage_browser.enable_file_download_button = false;

    render(
      <StorageFilePage fileName={mockFileName} fileStats={mockFileStats} onReload={mockReload} />
    );

    expect(screen.queryByRole('button', { name: 'Download' })).toBeNull();
    expect(screen.queryByRole('link', { name: 'Download' })).toBeNull();
  });

  // TODO: fix this test when mocking of useLoadData onSuccess callback is mproperly mocked
  it.skip('should render a textarea for text files', () => {
    render(
      <StorageFilePage fileName={mockFileName} fileStats={mockFileStats} onReload={mockReload} />
    );

    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveValue('Initial file content');
  });

  it('should render an image for image files', () => {
    render(
      <StorageFilePage
        fileName="imagefile.png"
        fileStats={{ ...mockFileStats, path: '/path/to/imagefile.png' }}
        onReload={mockReload}
      />
    );

    const img = screen.getByRole('img');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', expect.stringContaining('imagefile.png'));
  });

  it('should render a preview button for document files', () => {
    render(
      <StorageFilePage
        fileName="documentfile.pdf"
        fileStats={{ ...mockFileStats, path: '/path/to/documentfile.pdf' }}
        onReload={mockReload}
      />
    );

    expect(screen.getByRole('button', { name: /preview document/i })).toBeInTheDocument();
  });

  it('should render an audio player for audio files', () => {
    render(
      <StorageFilePage
        fileName="audiofile.mp3"
        fileStats={{ ...mockFileStats, path: '/path/to/audiofile.mp3' }}
        onReload={mockReload}
      />
    );

    const audio = screen.getByTestId('preview__content__audio'); // audio tag can't be access using getByRole
    expect(audio).toBeInTheDocument();
    expect(audio.children[0]).toHaveAttribute('src', expect.stringContaining('audiofile.mp3'));
  });

  it('should render a video player for video files', () => {
    render(
      <StorageFilePage
        fileName="videofile.mp4"
        fileStats={{ ...mockFileStats, path: '/path/to/videofile.mp4' }}
        onReload={mockReload}
      />
    );

    const video = screen.getByTestId('preview__content__video'); // video tag can't be access using getByRole
    expect(video).toBeInTheDocument();
    expect(video.children[0]).toHaveAttribute('src', expect.stringContaining('videofile.mp4'));
  });

  it('should display a message for unsupported file types', () => {
    render(
      <StorageFilePage
        fileStats={{
          ...mockFileStats,
          path: '/path/to/unsupportedfile.xyz'
        }}
        fileName="unsupportedfile.xyz"
        onReload={mockReload}
      />
    );

    expect(screen.getByText(/preview not available for this file/i)).toBeInTheDocument();
  });
});
