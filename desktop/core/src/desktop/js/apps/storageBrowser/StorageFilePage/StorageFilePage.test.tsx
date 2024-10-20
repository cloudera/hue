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
import { PathAndFileData } from '../../../reactComponents/FileChooser/types';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { DOWNLOAD_API_URL } from '../../../reactComponents/FileChooser/api';
import huePubSub from '../../../utils/huePubSub';

jest.mock('../../../utils/dateTimeUtils', () => ({
  ...jest.requireActual('../../../utils/dateTimeUtils'),
  formatTimestamp: () => {
    return 'April 8, 2021 at 00:00 AM';
  }
}));

jest.mock('../../../utils/huePubSub', () => ({
  publish: jest.fn()
}));

// Mock data for fileData
const mockFileData: PathAndFileData = {
  path: '/path/to/file.txt',
  stats: {
    size: 123456,
    user: 'testuser',
    group: 'testgroup',
    mtime: '1617877200',
    atime: '1617877200',
    mode: 33188,
    path: '/path/to/file.txt',
    aclBit: false
  },
  rwx: 'rwxr-xr-x',
  breadcrumbs: [],
  view: {
    contents: 'Initial file content'
  },
  files: [],
  page: {
    number: 1,
    num_pages: 1,
    previous_page_number: 1,
    next_page_number: 1,
    start_index: 1,
    end_index: 1,
    total_count: 1
  },
  pagesize: 100,
  show_download_button: true
};

describe('StorageFilePage', () => {
  it('renders file metadata and content', () => {
    render(<StorageFilePage fileData={mockFileData} />);

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
    expect(screen.getByText('Initial file content')).toBeInTheDocument();
  });

  it('shows edit button and hides save/cancel buttons initially', () => {
    render(<StorageFilePage fileData={mockFileData} />);

    expect(screen.getByRole('button', { name: 'Edit' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Save' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Cancel' })).toBeNull();
  });

  it('shows save and cancel buttons when editing', async () => {
    const user = userEvent.setup();
    render(<StorageFilePage fileData={mockFileData} />);

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

  it('updates textarea value and calls handleSave', async () => {
    const user = userEvent.setup();
    render(<StorageFilePage fileData={mockFileData} />);

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

  it('cancels editing and reverts textarea value', async () => {
    const user = userEvent.setup();
    render(<StorageFilePage fileData={mockFileData} />);

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

  it('downloads file when download button is clicked', async () => {
    const user = userEvent.setup();
    render(<StorageFilePage fileData={mockFileData} />);

    await user.click(screen.getByRole('button', { name: 'Download' }));

    expect(huePubSub.publish).toHaveBeenCalledWith('hue.global.info', {
      message: 'Downloading your file, Please wait...'
    });

    const downloadLink = screen.getByRole('link', { name: 'Download' });
    expect(downloadLink).toHaveAttribute('href', `${DOWNLOAD_API_URL}${mockFileData.path}`);
  });

  it('downloads file when download button is clicked', async () => {
    const user = userEvent.setup();
    render(<StorageFilePage fileData={mockFileData} />);

    await user.click(screen.getByRole('button', { name: 'Download' }));

    expect(huePubSub.publish).toHaveBeenCalledWith('hue.global.info', {
      message: 'Downloading your file, Please wait...'
    });

    const downloadLink = screen.getByRole('link', { name: 'Download' });
    expect(downloadLink).toHaveAttribute('href', `${DOWNLOAD_API_URL}${mockFileData.path}`);
  });

  it('does not render the download button when show_download_button is false', () => {
    const mockFileDataWithoutDownload = {
      ...mockFileData,
      show_download_button: false
    };

    render(<StorageFilePage fileData={mockFileDataWithoutDownload} />);

    expect(screen.queryByRole('button', { name: 'Download' })).toBeNull();
    expect(screen.queryByRole('link', { name: 'Download' })).toBeNull();
  });
});
