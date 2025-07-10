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
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Overview from './OverviewTab';
import Examples from './Examples';
import {
  INSTALL_APP_EXAMPLES_API_URL,
  INSTALL_AVAILABLE_EXAMPLES_API_URL
} from '../Components/utils';
import { get, post } from '../../../api/utils';
import * as hueConfigModule from '../../../config/hueConfig';

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

    test('fetch and display available apps', async () => {
      render(<Examples />);
      expect(get).toHaveBeenCalledWith(INSTALL_AVAILABLE_EXAMPLES_API_URL, {});
      for (const [, appName] of Object.entries(availableAppsResponse.apps)) {
        expect(await screen.findByText(appName)).toBeInTheDocument();
      }
    });

    test('post call to install apps without data like hive when the install button is clicked', async () => {
      render(<Examples />);
      const installButton = await screen.findByText('Hive');
      await userEvent.click(installButton);
      expect(post).toHaveBeenCalledWith(INSTALL_APP_EXAMPLES_API_URL, { app_name: 'hive' });
    });

    test('post call to install Solr Search example and its data when the install button is clicked', async () => {
      render(<Examples />);
      const solrData = ['log_analytics_demo', 'twitter_demo', 'yelp_demo'];
      const installButton = await screen.findByText('Solr Search');
      await userEvent.click(installButton);
      for (const dataEntry of solrData) {
        expect(post).toHaveBeenCalledWith(INSTALL_APP_EXAMPLES_API_URL, {
          app_name: 'search',
          data: dataEntry
        });
      }
      expect(post).toHaveBeenCalledTimes(solrData.length);
    });
  });
});
