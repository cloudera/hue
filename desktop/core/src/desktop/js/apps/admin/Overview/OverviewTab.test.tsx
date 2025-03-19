// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import '@testing-library/jest-dom';
import React from 'react';
import { queryByText, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Overview from './OverviewTab';
import Analytics from './Analytics';
import saveCollectUsagePreference from '../Overview/Analytics';
import * as hueConfigModule from '../../../config/hueConfig';

import { post } from '../../../api/utils';

jest.mock('./ConfigStatus', () => () => <div>MockedConfigStatusComponent</div>);
jest.mock('./Examples', () => () => <div>MockedExamplesComponent</div>);
jest.mock('./Analytics', () => () => <div>MockedAnalyticsComponent</div>);

jest.mock('../../../config/hueConfig', () => ({
  getLastKnownConfig: jest.fn()
}));

describe('OverviewTab', () => {
beforeEach(() => {
  (hueConfigModule.getLastKnownConfig as jest.Mock).mockReturnValue({
    hue_config: { is_admin: true }
  });
});
   afterEach(() => {
     jest.clearAllMocks();
   });

  test('renders the Tabs with the correct tab labels', () => {
    render(<Overview />);
    expect(screen.getByText('ConfigStatus')).toBeInTheDocument();
    expect(screen.getByText('Examples')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();
  });

  test('renders the ConfigStatus tab by default', () => {
    render(<Overview />);
    expect(screen.getByText('MockedConfigStatusComponent')).toBeInTheDocument();
    expect(screen.queryByText('MockedExamplesComponent')).not.toBeInTheDocument();
    expect(screen.queryByText('MockedAnalyticsComponent')).not.toBeInTheDocument();
  });

  test('shows the trademark text', () => {
    render(<Overview />);
    expect(
      screen.getByText('Hue and the Hue logo are trademarks of Cloudera, Inc.')
    ).toBeInTheDocument();
  });


  test('it should not render Overview for non-admin users', () => {
    (hueConfigModule.getLastKnownConfig as jest.Mock).mockReturnValue({
      hue_config: { is_admin: false }
    });

    const { queryByText } = render(<Overview />);
    const trademarkText = queryByText('Hue and the Hue logo are trademarks of Cloudera, Inc.');
    expect(trademarkText).toBeNull();
  });


  // jest.mock('../Overview/Analytics', () => ({
  //   __esModule: true,
  //   saveCollectUsagePreference: jest.fn(() => Promise.resolve({ status: 0 }))
  // }));
  // jest.mock('../../../api/utils', () => ({
  //   post: jest.fn(() => Promise.resolve({ status: 0 }))
  // }));

  //   describe('Analytics Component', () => {
  //      beforeEach(() => {
  //        jest.clearAllMocks();
  //      });
  //  test('renders Analytics tab and can interact with the checkbox', async () => {
  //     render(<Analytics />);
  //  const checkbox = screen.getByRole('checkbox', {
  //    name: /help improve hue with anonymous usage analytics\./i
  //  });

  //     expect(checkbox).not.toBeChecked();
  //     await userEvent.click(checkbox);
  //     await waitFor(() => expect(checkbox).toBeChecked());
  //   expect(saveCollectUsagePreference).toHaveBeenCalledWith(true);

  //     await userEvent.click(checkbox);
  //     await waitFor(() => expect(checkbox).not.toBeChecked());
  //   expect(saveCollectUsagePreference).toHaveBeenCalledWith(false);
  //   });
  // });
  // describe('Analytics Component', () => {
  //   beforeEach(() => {
  //     jest.clearAllMocks();
  //   });

  //   test('renders Analytics tab and can interact with the checkbox', async () => {
  //     render(<Analytics />);
  //     const checkbox = screen.getByRole('checkbox', {
  //       name: /help improve hue with anonymous usage analytics\./i
  //     });

  //     expect(checkbox).not.toBeChecked();
  //     await userEvent.click(checkbox);
  //     await waitFor(() => expect(checkbox).toBeChecked());

  //     // Now that we are mocking 'post', we assert that the post API call was made
  //     expect(post).toHaveBeenCalledWith('/about/update_preferences', { collect_usage: 'on' });

  //     await userEvent.click(checkbox);
  //     await waitFor(() => expect(checkbox).not.toBeChecked());

  //     // Again we check that the 'post' was called with the new state ('null' for off)
  //     expect(post).toHaveBeenCalledWith('/about/update_preferences', { collect_usage: null });
  //   });
  // });
});

//click on hive app and api of hive is called (toHaveBeenCalled())
