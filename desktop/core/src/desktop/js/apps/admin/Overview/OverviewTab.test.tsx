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
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Overview from './OverviewTab';
import Analytics from './Analytics';
// import ApiHelper from '../../../api/apiHelper';
// import saveCollectUsagePreference from 

jest.mock('./ConfigStatus', () => () => <div>MockedConfigStatusComponent</div>);
jest.mock('./Examples', () => () => <div>MockedExamplesComponent</div>);
jest.mock('./Analytics', () => () => <div>MockedAnalyticsComponent</div>);

  jest.mock('../../../api/apiHelper', () => ({
    ...jest.requireActual('../../../api/apiHelper'),
    updatePreferences: jest.fn(() => Promise.resolve({ status: 0, data: 'Success message' }))
  }));
describe('OverviewTab', () => {
  beforeEach(() => {
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
    expect(screen.getByText('Hue and the Hue logo are trademarks of Cloudera, Inc.')
    ).toBeInTheDocument();
  });

  jest.mock('../../../config/hueConfig', () => ({
    getLastKnownConfig: () => ({ hue_config: { is_admin: false } })
  }));

  test('it should not render Overview for non-admin users', () => {
    const { queryByTestId } = render(<Overview />);
    const overviewComponent = queryByTestId('overview-component');

    expect(overviewComponent).toBeNull();
  });


  //verify table contents

    // describe('Analytics Component', () => {
    //   test('renders Analytics tab and can interact with the checkbox', async () => {
    //     render(<Overview />);
    //     const analyticsTabButton = screen.getByText('Analytics');
    //     userEvent.click(analyticsTabButton); 

    //     const checkbox = await screen.findByTitle('Check to enable usage analytics');

    //     expect(checkbox).not.toBeChecked(); 
    //     userEvent.click(checkbox);
    //     await waitFor(() => expect(checkbox).toBeChecked());
    //     expect(ApiHelper.updatePreferences).toHaveBeenCalledWith({ collect_usage: 'on' });
    //     userEvent.click(checkbox);
    //     await waitFor(() => expect(checkbox).not.toBeChecked()); 
    //     expect(ApiHelper.updatePreferences).toHaveBeenCalledWith({ collect_usage: null });
    //   });
    // });
});

//click on hive app and api of hive is called (toHaveBeenCalled())