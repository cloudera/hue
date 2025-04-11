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
import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import FileAndFolderActions from './FileAndFolderActions';
import { StorageDirectoryTableData } from '../../../types';
import { get } from '../../../../../api/utils';
import { DOWNLOAD_API_URL } from '../../../api';

jest.mock('../../../../../api/utils', () => ({
  get: jest.fn()
}));

jest.mock('../../../../../utils/huePubSub', () => ({
  publish: jest.fn()
}));

const mockLastConfig = {
  storage_browser: {
    enable_file_download_button: true,
    enable_extract_uploaded_archive: true
  }
};
jest.mock('config/hueConfig', () => ({
  getLastKnownConfig: jest.fn(() => mockLastConfig)
}));

const mockGet = get as jest.MockedFunction<typeof get>;

describe('FileAndFolderActions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  //View summary option is enabled and added to the actions menu when the row data is either hdfs/ofs and a single file
  const mockTwoRecords: StorageDirectoryTableData[] = [
    {
      name: 'test.txt',
      size: '0 Bytes',
      user: 'demo',
      group: 'demo',
      permission: 'drwxr-xr-x',
      mtime: 'May 12, 2024 10:37 PM',
      type: 'file',
      path: '/path/to/folder/test.txt',
      replication: 0
    },
    {
      name: 'testFolder',
      size: '0 Bytes',
      user: 'demo',
      group: 'demo',
      permission: 'drwxr-xr-x',
      mtime: 'May 12, 2024 10:37 PM',
      type: 'dir',
      path: '/path/to/folder/testFolder',
      replication: 0
    }
  ];

  const mockRecord: StorageDirectoryTableData = mockTwoRecords[0];

  const mockOnActionSuccess = jest.fn();
  const mockOnActionError = jest.fn();
  const mockConfig = {
    isTrashEnabled: true,
    isHdfsSuperuser: true,
    groups: ['hue'],
    users: ['hue'],
    superuser: 'hue',
    supergroup: 'hue'
  };

  const setUpActionMenu = async (
    records: StorageDirectoryTableData[],
    recordPath?: string,
    recordType?: string
  ) => {
    const user = userEvent.setup();
    const selectedFiles =
      records.length === 1
        ? [
            {
              ...records[0],
              path: recordPath ?? records[0].path,
              type: recordType ?? records[0].type
            }
          ]
        : records;
    const { getByRole } = render(
      <FileAndFolderActions
        config={mockConfig}
        onActionError={mockOnActionError}
        onActionSuccess={mockOnActionSuccess}
        selectedFiles={selectedFiles}
        currentPath="/path/to/folder"
      />
    );
    await act(() => user.click(getByRole('button')));
  };

  describe('Summary option', () => {
    beforeAll(() => {
      jest.clearAllMocks();
    });

    beforeEach(() => {
      mockGet.mockResolvedValue(mockSummary);
    });

    afterEach(() => {
      jest.clearAllMocks();
    });

    const mockSummary = {
      summary: {
        directoryCount: 0,
        ecPolicy: 'Replicated',
        fileCount: 1,
        length: 0,
        quota: -1,
        spaceConsumed: 0,
        spaceQuota: -1,
        typeQuota: -1,
        replication: 3
      }
    };

    it('should not render summary option when there are multiple records selected', async () => {
      await setUpActionMenu(mockTwoRecords);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Summary' })).toBeNull());
    });

    it('should render summary option when record is a hdfs file', async () => {
      await setUpActionMenu([mockRecord], '/user/demo/test', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Summary' })).not.toBeNull());
    });

    it('should render summary option when record is a ofs file', async () => {
      await setUpActionMenu([mockRecord], 'ofs://demo/test', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Summary' })).not.toBeNull());
    });

    it('should not render summary option when record is a hdfs folder', async () => {
      await setUpActionMenu([mockRecord], '/user/demo/test', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Summary' })).toBeNull());
    });

    it('should not render summary option when record is a an abfs file', async () => {
      await setUpActionMenu([mockRecord], 'abfs://demo/test', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Summary' })).toBeNull());
    });
  });

  describe('Rename option', () => {
    it('should not render rename option when there are multiple records selected', async () => {
      await setUpActionMenu(mockTwoRecords);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull());
    });
    it('should not render rename option when selected record is a abfs root folder', async () => {
      await setUpActionMenu([mockRecord], 'abfs://', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull());
    });

    it('should not render rename option when selected record is a gs root folder', async () => {
      await setUpActionMenu([mockRecord], 'gs://', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull());
    });

    it('should not render rename option when selected record is a s3 root folder', async () => {
      await setUpActionMenu([mockRecord], 's3a://', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull());
    });

    it('should not render rename option when selected record is a ofs root folder', async () => {
      await setUpActionMenu([mockRecord], 'ofs://', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull());
    });

    it('should not render rename option when selected record is a ofs service ID folder', async () => {
      await setUpActionMenu([mockRecord], 'ofs://serviceID', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull());
    });

    it('should not render rename option when selected record is a ofs volume folder', async () => {
      await setUpActionMenu([mockRecord], 'ofs://serviceID/volume', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull());
    });

    it('should render rename option when selected record is a file or a folder', async () => {
      await setUpActionMenu([mockRecord], 'abfs://test', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Rename' })).not.toBeNull());
    });
  });

  describe('Set replication option', () => {
    it('should not render set replication option when there are multiple records selected', async () => {
      await setUpActionMenu(mockTwoRecords);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).toBeNull());
    });

    it('should render set replication option when selected record is a hdfs file', async () => {
      await setUpActionMenu([mockRecord], 'hdfs://test', 'file');
      waitFor(() =>
        expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).not.toBeNull()
      );
    });

    it('should not render set replication option when selected record is a hdfs folder', async () => {
      await setUpActionMenu([mockRecord], 'hdfs://', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).toBeNull());
    });

    it('should not render set replication option when selected record is a gs file/folder', async () => {
      await setUpActionMenu([mockRecord], 'gs://', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).toBeNull());
    });

    it('should not render set replication option when selected record is a s3 file/folder', async () => {
      await setUpActionMenu([mockRecord], 's3a://', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).toBeNull());
    });

    it('should not render set replication option when selected record is a ofs file/folder', async () => {
      await setUpActionMenu([mockRecord], 'ofs://', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).toBeNull());
    });
  });

  describe('Delete option', () => {
    it('should render delete option for multiple selected records', async () => {
      await setUpActionMenu(mockTwoRecords, mockRecord.path);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Delete' })).not.toBeNull());
    });

    it('should render delete option for a single selected file/folder', async () => {
      await setUpActionMenu([mockRecord], '/user/demo/test', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Delete' })).not.toBeNull());
    });
  });

  describe('Download option', () => {
    const originalLocation = window.location;
    beforeEach(() => {
      Object.defineProperty(window, 'location', {
        writable: true,
        value: { href: '' }
      });
    });

    afterAll(() => {
      Object.defineProperty(window, 'location', {
        writable: true,
        value: originalLocation
      });
    });

    it('should not render download option for multiple selected records', async () => {
      await setUpActionMenu(mockTwoRecords);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Download' })).toBeNull());
    });

    it('should render download option for a single selected file', async () => {
      await setUpActionMenu([mockRecord], '/user/demo/test', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Download' })).not.toBeNull());
    });

    it('should not render download option for a folder', async () => {
      const mockFolder = { ...mockRecord, type: 'dir' };
      await setUpActionMenu([mockFolder], '/user/demo/test', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Download' })).toBeNull());
    });

    it('should not render download option when enable_file_download_button is false', async () => {
      mockLastConfig.storage_browser.enable_file_download_button = false;
      await setUpActionMenu([mockRecord], '/user/demo/test', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Download' })).toBeNull());
      mockLastConfig.storage_browser.enable_file_download_button = true;
    });

    it('should trigger file download when download option is clicked for a file', async () => {
      const user = userEvent.setup();
      await setUpActionMenu([mockRecord], mockRecord.path, 'file');
      await user.click(screen.getByRole('menuitem', { name: 'Download' }));
      waitFor(() => expect(window.location.href).toContain(DOWNLOAD_API_URL));
    });
  });

  describe('Copy Action', () => {
    it('should render copy option when record is a file', async () => {
      await setUpActionMenu([mockRecord], '/user/demo/test', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Copy' })).not.toBeNull());
    });

    it('should render copy option when record is a folder', async () => {
      await setUpActionMenu([mockRecord], '/user/demo/test', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Copy' })).not.toBeNull());
    });

    it('should render copy option when multiple records are selected', async () => {
      await setUpActionMenu(mockTwoRecords);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Copy' })).not.toBeNull());
    });
  });

  describe('Move Action', () => {
    it('should render move option when record is a file', async () => {
      await setUpActionMenu([mockRecord], '/user/demo/test', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Move' })).not.toBeNull());
    });

    it('should render move option when record is a folder', async () => {
      await setUpActionMenu([mockRecord], '/user/demo/test', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Move' })).not.toBeNull());
    });

    it('should render move option when multiple records are selected', async () => {
      await setUpActionMenu(mockTwoRecords);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Move' })).not.toBeNull());
    });
  });

  describe('Compress Action', () => {
    it('should render compress option when record is a hdfs file', async () => {
      await setUpActionMenu([mockRecord], mockRecord.path, mockRecord.type);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Compress' })).not.toBeNull());
    });

    it('should render compress option when multiple records are hdfs file', async () => {
      await setUpActionMenu(mockTwoRecords);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Compress' })).not.toBeNull());
    });

    it('should render compress option when record is not hdfs file', async () => {
      await setUpActionMenu([mockRecord], 's3a://', 'dir');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Compress' })).toBeNull());
    });

    it('should not render compress option when enable_extract_uploaded_archive is false', async () => {
      mockLastConfig.storage_browser.enable_extract_uploaded_archive = false;
      await setUpActionMenu(mockTwoRecords);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Compress' })).toBeNull());
      mockLastConfig.storage_browser.enable_extract_uploaded_archive = true;
    });
  });

  describe('Extract Action', () => {
    it('should render extract option when record is a compressed file', async () => {
      mockRecord.path = '/user/demo/test.zip';
      await setUpActionMenu([mockRecord], '/user/demo/test.zip', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Extract' })).not.toBeNull());
    });

    it('should not render extract option when multiple records are files', async () => {
      await setUpActionMenu(mockTwoRecords);
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Extract' })).toBeNull());
    });

    it('should not render extract option when file type is not supported', async () => {
      mockRecord.path = '/user/demo/test.zip1';
      await setUpActionMenu([mockRecord], '/user/demo/test.zip1', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Extract' })).toBeNull());
    });

    it('should not render extract option when enable_extract_uploaded_archive is false', async () => {
      mockLastConfig.storage_browser.enable_extract_uploaded_archive = false;
      await setUpActionMenu([mockRecord], '/user/demo/test.zip', 'file');
      waitFor(() => expect(screen.queryByRole('menuitem', { name: 'Extract' })).toBeNull());
      mockLastConfig.storage_browser.enable_extract_uploaded_archive = true;
    });
  });
});
