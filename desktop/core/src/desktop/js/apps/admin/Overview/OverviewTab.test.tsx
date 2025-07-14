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
import {
  INSTALL_APP_EXAMPLES_API_URL,
  INSTALL_AVAILABLE_EXAMPLES_API_URL,
  USAGE_ANALYTICS_API_URL
} from '../Components/utils';
import { get, post } from '../../../api/utils';
import * as hueConfigModule from '../../../config/hueConfig';
import huePubSub from '../../../utils/huePubSub';

jest.mock('../../../api/utils', () => ({
  post: jest.fn(),
  get: jest.fn()
}));

jest.mock('./ConfigStatus', () => () => <div>MockedConfigStatusComponent</div>);

jest.mock('../../../config/hueConfig', () => ({
  getLastKnownConfig: jest.fn()
}));

jest.mock('../../../utils/huePubSub', () => ({
  publish: jest.fn()
}));

jest.mock(
  '../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper',
  () =>
    ({ children, loading, errors }) => (
      <div data-testid="loading-error-wrapper">
        {loading && <div data-testid="loading-spinner">Loading...</div>}
        {errors
          ?.filter(error => error.enabled)
          .map((error, index) => (
            <div key={index} data-testid="error-message">
              {error.message}
            </div>
          ))}
        {children}
      </div>
    )
);

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

  describe('Analytics component', () => {
    const mockAnalyticsData = { collectUsage: true };
    const mockAnalyticsDataDisabled = { collectUsage: false };

    beforeEach(() => {
      (get as jest.Mock).mockImplementation(url => {
        if (url === USAGE_ANALYTICS_API_URL) {
          return Promise.resolve(mockAnalyticsData);
        }
        return Promise.reject();
      });
      (post as jest.Mock).mockImplementation(() => Promise.resolve({ collect_usage: true }));
    });

    test('renders analytics title and checkbox', async () => {
      render(<Analytics />);

      expect(screen.getByText('Anonymous usage analytics')).toBeInTheDocument();
      expect(
        screen.getByLabelText('Help improve Hue with anonymous usage analytics.')
      ).toBeInTheDocument();
      expect(screen.getByRole('checkbox')).toBeInTheDocument();
    });

    test('fetches and displays analytics data on mount', async () => {
      render(<Analytics />);

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(USAGE_ANALYTICS_API_URL, undefined, expect.any(Object));
      });

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(true);
      });
    });

    test('checkbox reflects analytics data state when disabled', async () => {
      (get as jest.Mock).mockResolvedValue(mockAnalyticsDataDisabled);

      render(<Analytics />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(false);
      });
    });

    test('shows loading state during initial data fetch', () => {
      (get as jest.Mock).mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<Analytics />);

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    test('shows error message when data fetch fails', async () => {
      const errorMessage = 'Failed to fetch analytics data';
      (get as jest.Mock).mockRejectedValue(errorMessage);

      render(<Analytics />);

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
      });
    });

    test('handles checkbox toggle to enable analytics', async () => {
      (get as jest.Mock).mockResolvedValue(mockAnalyticsDataDisabled);

      render(<Analytics />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(false);
      });

      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(post).toHaveBeenCalledWith(
          USAGE_ANALYTICS_API_URL,
          { collect_usage: true },
          expect.any(Object)
        );
      });
    });

    test('handles checkbox toggle to disable analytics', async () => {
      render(<Analytics />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(true);
      });

      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(post).toHaveBeenCalledWith(
          USAGE_ANALYTICS_API_URL,
          { collect_usage: false },
          expect.any(Object)
        );
      });
    });

    test('disables checkbox during save operation', async () => {
      (post as jest.Mock).mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<Analytics />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(true);
      });

      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(checkbox.disabled).toBe(true);
      });
    });

    test('shows loading state during save operation', async () => {
      (post as jest.Mock).mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<Analytics />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(true);
      });

      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      });
    });

    test('shows error message when save operation fails', async () => {
      const errorMessage = 'Failed to update analytics preference';
      (post as jest.Mock).mockRejectedValue(errorMessage);

      render(<Analytics />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(true);
      });

      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
      });
    });

    test('publishes success message when analytics are enabled', async () => {
      (get as jest.Mock).mockResolvedValue(mockAnalyticsDataDisabled);
      (post as jest.Mock).mockResolvedValue({ collect_usage: true });

      render(<Analytics />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(false);
      });

      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(huePubSub.publish).toHaveBeenCalledWith('hue.global.info', {
          message: 'Analytics have been activated.'
        });
      });
    });

    test('publishes success message when analytics are disabled', async () => {
      (post as jest.Mock).mockResolvedValue({ collect_usage: false });

      render(<Analytics />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(true);
      });

      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(huePubSub.publish).toHaveBeenCalledWith('hue.global.info', {
          message: 'Analytics have been deactivated.'
        });
      });
    });

    test('reloads data after successful save', async () => {
      (post as jest.Mock).mockResolvedValue({ collect_usage: false });

      render(<Analytics />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(true);
      });

      // Clear the initial get call
      (get as jest.Mock).mockClear();

      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(USAGE_ANALYTICS_API_URL, undefined, expect.any(Object));
      });
    });

    test('handles undefined analytics data gracefully', async () => {
      (get as jest.Mock).mockResolvedValue({});

      render(<Analytics />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await waitFor(() => {
        expect(checkbox.checked).toBe(false);
      });
    });

    test('handles multiple error states simultaneously', async () => {
      const fetchError = 'Fetch failed';
      const saveError = 'Save failed';

      (get as jest.Mock).mockRejectedValue(fetchError);
      (post as jest.Mock).mockRejectedValue(saveError);

      render(<Analytics />);

      // First error from fetch
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
      });

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      await userEvent.click(checkbox);

      // Should show both errors
      await waitFor(() => {
        const errorMessages = screen.getAllByTestId('error-message');
        expect(errorMessages).toHaveLength(2);
      });
    });
  });
});
