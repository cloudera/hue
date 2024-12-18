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
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import StorageBrowserActions from './StorageBrowserActions';
import { StorageBrowserTableData } from '../../../../reactComponents/FileChooser/types';
import { get } from '../../../../api/utils';

jest.mock('../../../../api/utils', () => ({
  get: jest.fn()
}));

const mockGet = get as jest.MockedFunction<typeof get>;
describe('StorageBrowserRowActions', () => {
  //View summary option is enabled and added to the actions menu when the row data is either hdfs/ofs and a single file
  const mockRecord: StorageBrowserTableData = {
    name: 'test',
    size: '0\u00a0bytes',
    user: 'demo',
    group: 'demo',
    permission: 'drwxr-xr-x',
    mtime: 'May 12, 2024 10:37 PM',
    type: '',
    path: '',
    replication: 0
  };
  const mockTwoRecords: StorageBrowserTableData[] = [
    {
      name: 'test',
      size: '0\u00a0bytes',
      user: 'demo',
      group: 'demo',
      permission: 'drwxr-xr-x',
      mtime: 'May 12, 2024 10:37 PM',
      type: 'file',
      path: '',
      replication: 0
    },
    {
      name: 'testFolder',
      size: '0\u00a0bytes',
      user: 'demo',
      group: 'demo',
      permission: 'drwxr-xr-x',
      mtime: 'May 12, 2024 10:37 PM',
      type: 'dir',
      path: '',
      replication: 0
    }
  ];

  const setLoadingFiles = jest.fn();
  const onSuccessfulAction = jest.fn();

  const setUpActionMenu = async (
    records: StorageBrowserTableData[],
    recordPath?: string,
    recordType?: string
  ) => {
    const user = userEvent.setup();
    if (recordPath) {
      records[0].path = recordPath;
    }
    if (recordType) {
      records[0].type = recordType;
    }
    const { getByRole } = render(
      <StorageBrowserActions
        setLoadingFiles={setLoadingFiles}
        onSuccessfulAction={onSuccessfulAction}
        selectedFiles={records}
      />
    );
    await user.click(getByRole('button'));
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
    test('does not render view summary option when there are multiple records selected', async () => {
      await setUpActionMenu(mockTwoRecords);
      expect(screen.queryByRole('menuitem', { name: 'View Summary' })).toBeNull();
    });

    test('renders view summary option when record is a hdfs file', async () => {
      await setUpActionMenu([mockRecord], '/user/demo/test', 'file');
      expect(screen.queryByRole('menuitem', { name: 'View Summary' })).not.toBeNull();
    });

    test('renders view summary option when record is a ofs file', async () => {
      await setUpActionMenu([mockRecord], 'ofs://demo/test', 'file');
      expect(screen.queryByRole('menuitem', { name: 'View Summary' })).not.toBeNull();
    });

    test('does not render view summary option when record is a hdfs folder', async () => {
      await setUpActionMenu([mockRecord], '/user/demo/test', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'View Summary' })).toBeNull();
    });

    test('does not render view summary option when record is a an abfs file', async () => {
      await setUpActionMenu([mockRecord], 'abfs://demo/test', 'file');
      expect(screen.queryByRole('menuitem', { name: 'View Summary' })).toBeNull();
    });

    test('renders summary modal when view summary option is clicked', async () => {
      const user = userEvent.setup();
      await setUpActionMenu([mockRecord], '/user/demo/test', 'file');
      await user.click(screen.queryByRole('menuitem', { name: 'View Summary' })!);
      expect(await screen.findByText('Summary for /user/demo/test')).toBeInTheDocument();
    });
  });

  describe('Rename option', () => {
    test('does not render rename option when there are multiple records selected', async () => {
      await setUpActionMenu(mockTwoRecords);
      expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });
    test('does not render rename option when selected record is a abfs root folder', async () => {
      await setUpActionMenu([mockRecord], 'abfs://', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('does not render rename option when selected record is a gs root folder', async () => {
      await setUpActionMenu([mockRecord], 'gs://', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('does not render rename option when selected record is a s3 root folder', async () => {
      await setUpActionMenu([mockRecord], 's3a://', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('does not render rename option when selected record is a ofs root folder', async () => {
      await setUpActionMenu([mockRecord], 'ofs://', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('does not render rename option when selected record is a ofs service ID folder', async () => {
      await setUpActionMenu([mockRecord], 'ofs://serviceID', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('does not render rename option when selected record is a ofs volume folder', async () => {
      await setUpActionMenu([mockRecord], 'ofs://serviceID/volume', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('renders rename option when selected record is a file or a folder', async () => {
      await setUpActionMenu([mockRecord], 'abfs://test', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Rename' })).not.toBeNull();
    });

    test('renders rename modal when rename option is clicked', async () => {
      const user = userEvent.setup();
      await setUpActionMenu([mockRecord], 'abfs://test', 'dir');
      await user.click(screen.queryByRole('menuitem', { name: 'Rename' }));
      expect(await screen.findByText('Enter new name here')).toBeInTheDocument();
    });
  });

  describe('Set replication option', () => {
    test('does not render set replication option when there are multiple records selected', async () => {
      await setUpActionMenu(mockTwoRecords);
      expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).toBeNull();
    });

    test('renders set replication option when selected record is a hdfs file', async () => {
      await setUpActionMenu([mockRecord], 'hdfs://test', 'file');
      expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).not.toBeNull();
    });

    test('does not render set replication option when selected record is a hdfs folder', async () => {
      await setUpActionMenu([mockRecord], 'hdfs://', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).toBeNull();
    });

    test('does not render set replication option when selected record is a gs file/folder', async () => {
      await setUpActionMenu([mockRecord], 'gs://', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).toBeNull();
    });

    test('does not render set replication option when selected record is a s3 file/folder', async () => {
      await setUpActionMenu([mockRecord], 's3a://', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).toBeNull();
    });

    test('does not render set replication option when selected record is a ofs file/folder', async () => {
      await setUpActionMenu([mockRecord], 'ofs://', 'dir');
      expect(screen.queryByRole('menuitem', { name: 'Set Replication' })).toBeNull();
    });

    test('renders set replication modal when set replication option is clicked', async () => {
      const user = userEvent.setup();
      await setUpActionMenu([mockRecord], 'hdfs://test', 'file');
      await user.click(screen.queryByRole('menuitem', { name: 'Set Replication' }));
      expect(await screen.findByText(/Setting Replication factor/i)).toBeInTheDocument();
    });
  });
});
