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
import { waitFor, screen, fireEvent, render } from '@testing-library/react';
import '@testing-library/jest-dom';

import { get } from '../../../api/utils';
import formatBytes from '../../../utils/formatBytes';
import SummaryModal from './SummaryModal';

// Mock the `get` function
jest.mock('../../../api/utils', () => ({
  get: jest.fn()
}));

const mockGet = get as jest.MockedFunction<typeof get>;

describe('SummaryModal', () => {
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
  test('renders path of file in title', async () => {
    const { getByText } = render(
      <SummaryModal showModal={true} onClose={() => {}} path="some/path" />
    );
    await waitFor(async () => {
      expect(getByText('Summary for some/path')).toBeInTheDocument();
    });
  });

  test('renders summary content after successful data fetching', async () => {
    const { getByText, getAllByText } = render(
      <SummaryModal showModal={true} onClose={() => {}} path="some/path" />
    );
    await waitFor(async () => {
      expect(getByText('DISKSPACE CONSUMED')).toBeInTheDocument();
      expect(getAllByText(formatBytes(mockSummary.summary.spaceConsumed))[0]).toBeInTheDocument();
    });
  });

  test('renders space consumed in Bytes after the values are formatted', async () => {
    render(<SummaryModal path={'/user/demo'} showModal={true} onClose={() => {}} />);
    const spaceConsumed = await screen.findAllByText('0 Byte');
    await waitFor(() => {
      expect(spaceConsumed[0]).toBeInTheDocument();
    });
  });

  test('should call onClose function when close button is clicked', async () => {
    const mockOnClose = jest.fn();
    const { getByText } = render(
      <SummaryModal showModal={true} onClose={mockOnClose} path="some/path" />
    );

    const closeButton = getByText('Close');
    expect(mockOnClose).not.toHaveBeenCalled();
    fireEvent.click(closeButton);
    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });
});
