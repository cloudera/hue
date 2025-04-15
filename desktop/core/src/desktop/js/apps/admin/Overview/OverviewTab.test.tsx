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
import {
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
    const availableAppsResponse = {
      apps: {
        hive: 'Hive',
        impala: 'Impala'
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

    test('post call to install app example when the install button is clicked', async () => {
      render(<Examples />);

      await waitFor(() => {
        const installButton = screen.getByText('Hive');
        fireEvent.click(installButton);
        expect(post).toHaveBeenCalledWith(INSTALL_APP_EXAMPLES_API_URL, { app_name: 'hive' });
      });
    });
  });
});
