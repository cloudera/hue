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

import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Overview from './OverviewTab';
import Examples from './Examples';
import Analytics from './Analytics';
import * as hueConfigModule from '../../../config/hueConfig';
import {
  UPDATE_USAGE_ANALYTICS_API_URL,
  INSTALL_APP_EXAMPLES_API_URL,
  INSTALL_AVAILABLE_EXAMPLES_API_URL
} from '../Components/utils';
import { get, post } from '../../../api/utils';

jest.mock('../../../api/utils', () => ({
  post: jest.fn(),
  get: jest.fn()
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

  describe('Analytics', () => {
    beforeEach(() => {
      (get as jest.Mock).mockResolvedValue({ analytics_enabled: false });
    });

    test('renders Analytics tab and can interact with the checkbox', async () => {
      render(<Analytics />);

      const checkbox = screen.getByLabelText(/Help improve Hue with anonymous usage analytics./i);

      expect(checkbox).not.toBeChecked();
      (post as jest.Mock).mockResolvedValueOnce({ analytics_enabled: true });
      await userEvent.click(checkbox);
      expect(checkbox).toBeChecked();
      expect(post).toHaveBeenCalledWith(UPDATE_USAGE_ANALYTICS_API_URL, {
        analytics_enabled: true
      });

      (post as jest.Mock).mockResolvedValueOnce({ analytics_enabled: false });
      await userEvent.click(checkbox);
      await waitFor(() => expect(checkbox).not.toBeChecked());
      expect(post).toHaveBeenCalledWith(UPDATE_USAGE_ANALYTICS_API_URL, {
        analytics_enabled: false
      });
    });
  });

  describe('Examples component', () => {
    const availableAppsResponse = {
      apps: {
        hive: 'Hive',
        impala: 'Impala',
        search: 'Solr Search'
      }
    };
    beforeEach(() => {
      (get as jest.Mock).mockImplementation(url => {
        if (url === INSTALL_AVAILABLE_EXAMPLES_API_URL) {
          return Promise.resolve(availableAppsResponse);
        }
        return Promise.reject();
      });

      (post as jest.Mock).mockImplementation(() =>
        Promise.resolve({ status: 0, message: 'Success' })
      );
    });

    afterEach(() => {
      jest.clearAllMocks();
    });

    test('fetch and display available apps', async () => {
      render(<Examples />);

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(INSTALL_AVAILABLE_EXAMPLES_API_URL, {});
        Object.entries(availableAppsResponse.apps).forEach(([, appName]) => {
          expect(screen.getByText(appName)).toBeInTheDocument();
        });
      });
    });

    test('post call to install apps without data like hive when the install button is clicked', async () => {
      render(<Examples />);

      await waitFor(() => {
        const installButton = screen.getByText('Hive');
        userEvent.click(installButton);
        expect(post).toHaveBeenCalledWith(INSTALL_APP_EXAMPLES_API_URL, { app_name: 'hive' });
      });
    });

    test('post call to install Solr Search example and its data when the install button is clicked', async () => {
      render(<Examples />);

      const solrData = ['log_analytics_demo', 'twitter_demo', 'yelp_demo'];
      await waitFor(() => screen.getByText('Solr Search'));
      const installButton = screen.getByText('Solr Search');
      userEvent.click(installButton);

      await waitFor(() => {
        solrData.forEach(dataEntry => {
          expect(post).toHaveBeenCalledWith(INSTALL_APP_EXAMPLES_API_URL, {
            app_name: 'search',
            data: dataEntry
          });
        });
      });

      expect(post).toHaveBeenCalledTimes(solrData.length);
    });
  });
});
