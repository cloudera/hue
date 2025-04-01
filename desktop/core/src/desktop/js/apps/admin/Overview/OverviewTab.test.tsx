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
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import Overview from './OverviewTab';
import * as hueConfigModule from '../../../config/hueConfig';
import Examples from './Examples';
import Analytics from './Analytics';
import { post } from '../../../api/utils';

jest.mock('../../../api/utils', () => ({
  post: jest.fn()
}));

jest.mock('./ConfigStatus', () => () => <div>MockedConfigStatusComponent</div>);

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
    expect(screen.getByText('Config Status')).toBeInTheDocument();
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

  describe('Analytics Component', () => {
    test('renders Analytics tab and can interact with the checkbox', async () => {
      (post as jest.Mock).mockResolvedValue({ status: 0, message: 'Success' });
      render(<Analytics />);
      const checkbox = screen.getByLabelText(/Help improve Hue with anonymous usage analytics./i);

      fireEvent.click(checkbox);
      await waitFor(() => expect(checkbox).toBeChecked());
      expect(post).toHaveBeenCalledWith('/about/update_preferences', {
        collect_usage: 'on'
      });
      fireEvent.click(checkbox);
      await waitFor(() => expect(checkbox).not.toBeChecked());
      expect(post).toHaveBeenCalledWith('/about/update_preferences', {
        collect_usage: null
      });
    });
  });

  describe('Examples component', () => {
    const exampleApps = [
      { id: 'hive', name: 'Hive', old_name: 'beeswax' },
      { id: 'impala', name: 'Impala' },
      {
        id: 'search',
        name: 'Solr Search',
        data: ['log_analytics_demo', 'twitter_demo', 'yelp_demo']
      },
      { id: 'spark', name: 'Spark', old_name: 'notebook' },
      { id: 'oozie', name: 'Oozie Editor/Dashboard' },
      { id: 'hbase', name: 'Hbase Browser' },
      { id: 'pig', name: 'Pig Editor' }
    ];

    const resolvedValue = { status: 0, message: 'Success' };

    exampleApps.forEach(appData => {
      test(`clicking the install button for '${appData.name}' makes an API call to '/api/v1/install_app_examples'`, async () => {
        (post as jest.Mock).mockResolvedValue(resolvedValue);
        render(<Examples />);

        const button = screen.getByText(appData.name);
        fireEvent.click(button);

        await waitFor(() => {
          if (appData.data) {
            expect(post).toHaveBeenCalledWith(
              '/api/v1/install_app_examples',
              {
                app_name: appData.id,
                data: appData.data
              },
              expect.anything()
            );
          } else {
            expect(post).toHaveBeenCalledWith(
              '/api/v1/install_app_examples',
              {
                app_name: appData.id
              },
              expect.anything()
            );
          }
        });
        (post as jest.Mock).mockClear();
      });
    });
  });
});
