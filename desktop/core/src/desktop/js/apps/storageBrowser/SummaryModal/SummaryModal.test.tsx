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
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import SummaryModal from './SummaryModal';
import * as StorageBrowserApi from '../../../reactComponents/FileChooser/api';
import { ContentSummary } from '../../../reactComponents/FileChooser/types';
import { CancellablePromise } from '../../../api/cancellablePromise';

describe('SummaryModal', () => {
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

  test('renders path of file in title', async () => {
    const onCloseMock = jest.fn();
    setUpMock();
    render(<SummaryModal path={'/user/demo'} showModal={true} onClose={onCloseMock} />);
    const title = await screen.findByText('Summary for /user/demo');
    await waitFor(() => {
      expect(title).toBeInTheDocument();
    });
  });

  test('renders space consumed in Bytes after the values are formatted', async () => {
    const onCloseMock = jest.fn();
    setUpMock();
    render(<SummaryModal path={'/user/demo'} showModal={true} onClose={onCloseMock} />);
    const spaceConsumed = await screen.findAllByText('0 Byte');
    await waitFor(() => {
      expect(spaceConsumed[0]).toBeInTheDocument();
    });
  });

  test('calls onClose when close button is clicked', async () => {
    const onCloseMock = jest.fn();
    setUpMock();
    const user = userEvent.setup();
    render(<SummaryModal path={'/user/demo'} showModal={true} onClose={onCloseMock} />);
    const closeButton = await screen.findByText('Close');
    expect(onCloseMock).not.toHaveBeenCalled();
    await user.click(closeButton);
    expect(onCloseMock).toHaveBeenCalled();
  });
});
