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
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import StorageBrowserActions from './StorageBrowserActions';
import { StorageBrowserTableData } from '../../../../reactComponents/FileChooser/types';
import * as StorageBrowserApi from '../../../../reactComponents/FileChooser/api';
import { CancellablePromise } from '../../../../api/cancellablePromise';

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
    path: ''
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
      path: ''
    },
    {
      name: 'testFolder',
      size: '0\u00a0bytes',
      user: 'demo',
      group: 'demo',
      permission: 'drwxr-xr-x',
      mtime: 'May 12, 2024 10:37 PM',
      type: 'dir',
      path: ''
    }
  ];

  const setLoadingFiles = jest.fn();
  const onSuccessfulAction = jest.fn();
  describe('Summary option', () => {
    let summaryApiMock;

    const mockSummaryData = {
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

    const setUpMock = () => {
      summaryApiMock = jest
        .spyOn(StorageBrowserApi, 'fetchContentSummary')
        .mockReturnValue(CancellablePromise.resolve<ContentSummary>(mockSummaryData));
    };

    afterEach(() => {
      summaryApiMock?.mockClear();
    });

    test('does not render view summary option when there are multiple records selected', async () => {
      const user = userEvent.setup();
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={mockTwoRecords}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'View Summary' })).toBeNull();
    });

    test('renders view summary option when record is a hdfs file', async () => {
      const user = userEvent.setup();
      mockRecord.path = '/user/demo/test';
      mockRecord.type = 'file';
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'View Summary' })).not.toBeNull();
    });

    test('renders view summary option when record is a ofs file', async () => {
      const user = userEvent.setup();
      mockRecord.path = 'ofs://demo/test';
      mockRecord.type = 'file';
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'View Summary' })).not.toBeNull();
    });

    test('does not render view summary option when record is a hdfs folder', async () => {
      const user = userEvent.setup();
      mockRecord.path = '/user/demo/test';
      mockRecord.type = 'dir';
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'View Summary' })).toBeNull();
    });

    test('does not render view summary option when record is a an abfs file', async () => {
      const user = userEvent.setup();
      mockRecord.path = 'abfs://demo/test';
      mockRecord.type = 'file';
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'View Summary' })).toBeNull();
    });

    test('renders summary modal when view summary option is clicked', async () => {
      const user = userEvent.setup();
      mockRecord.path = '/user/demo/test';
      mockRecord.type = 'file';
      setUpMock();
      const { getByRole, queryByRole, findByText } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      await user.click(queryByRole('menuitem', { name: 'View Summary' }));
      expect(await findByText('Summary for /user/demo/test')).toBeInTheDocument();
    });
  });

  describe('Rename option', () => {
    test('does not render view summary option when there are multiple records selected', async () => {
      const user = userEvent.setup();
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={mockTwoRecords}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });
    test('does not render rename option when selected record is a abfs root folder', async () => {
      const user = userEvent.setup();
      mockRecord.path = 'abfs://';
      mockRecord.type = 'dir';
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('does not render rename option when selected record is a gs root folder', async () => {
      const user = userEvent.setup();
      mockRecord.path = 'gs://';
      mockRecord.type = 'dir';
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('does not render rename option when selected record is a s3 root folder', async () => {
      const user = userEvent.setup();
      mockRecord.path = 's3a://';
      mockRecord.type = 'dir';
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('does not render rename option when selected record is a ofs service ID folder', async () => {
      const user = userEvent.setup();
      mockRecord.path = 'ofs://serviceID';
      mockRecord.type = 'dir';
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('does not render rename option when selected record is a ofs volume folder', async () => {
      const user = userEvent.setup();
      mockRecord.path = 'ofs://serviceID/volume';
      mockRecord.type = 'dir';
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'Rename' })).toBeNull();
    });

    test('renders rename option when selected record is a file or a folder', async () => {
      const user = userEvent.setup();
      mockRecord.path = 'abfs://test';
      mockRecord.type = 'dir';
      const { getByRole, queryByRole } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      expect(queryByRole('menuitem', { name: 'Rename' })).not.toBeNull();
    });

    test('renders rename modal when rename option is clicked', async () => {
      const user = userEvent.setup();
      mockRecord.path = 'abfs://test';
      mockRecord.type = 'dir';
      const { getByRole, queryByRole, findByText } = render(
        <StorageBrowserActions
          setLoadingFiles={setLoadingFiles}
          onSuccessfulAction={onSuccessfulAction}
          selectedFiles={[mockRecord]}
        />
      );
      await user.click(getByRole('button'));
      await user.click(queryByRole('menuitem', { name: 'Rename' }));
      expect(await findByText('Enter new name here')).toBeInTheDocument();
    });
  });
});
