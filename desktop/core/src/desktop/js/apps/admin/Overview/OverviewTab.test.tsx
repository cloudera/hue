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
import { get, post, sendApiRequest } from '../../../api/utils';
import * as hueConfigModule from '../../../config/hueConfig';
import huePubSub from '../../../utils/huePubSub';

jest.mock('../../../api/utils', () => ({
  post: jest.fn(),
  get: jest.fn(),
  sendApiRequest: jest.fn(),
  HttpMethod: {
    POST: 'post',
    PUT: 'put',
    PATCH: 'patch'
  }
}));

jest.mock('./ConfigStatus', () => () => <div>MockedConfigStatusComponent</div>);

jest.mock('../../../config/hueConfig', () => ({
  getLastKnownConfig: jest.fn()
}));

jest.mock('../../../utils/huePubSub', () => ({
  publish: jest.fn()
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

  it('renders the Tabs with the correct tab labels', () => {
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

    it('fetch and display available apps', async () => {
      render(<Examples />);
      expect(get).toHaveBeenCalledWith(INSTALL_AVAILABLE_EXAMPLES_API_URL, {});
      for (const [, appName] of Object.entries(availableAppsResponse.apps)) {
        expect(await screen.findByText(appName)).toBeInTheDocument();
      }
    });

    it('post call to install apps without data like hive when the install button is clicked', async () => {
      render(<Examples />);
      const installButton = await screen.findByText('Hive');
      await userEvent.click(installButton);
      expect(post).toHaveBeenCalledWith(INSTALL_APP_EXAMPLES_API_URL, { app_name: 'hive' });
    });

    it('post call to install Solr Search example and its data when the install button is clicked', async () => {
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
    const expectedFetchOptions = {
      silenceErrors: true,
      ignoreSuccessErrors: true
    };
    const expectedOptions = {
      silenceErrors: true,
      ignoreSuccessErrors: true,
      qsEncodeData: false
    };

    const renderAnalyticsAndWaitForLoad = async () => {
      render(<Analytics />);
      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(USAGE_ANALYTICS_API_URL, undefined, expectedFetchOptions);
      });
    };

    const getCheckboxElement = () => screen.getByRole('checkbox') as HTMLInputElement;

    const expectCheckboxState = async (checked: boolean) => {
      const checkbox = getCheckboxElement();
      await waitFor(() => {
        expect(checkbox.checked).toBe(checked);
      });
      return checkbox;
    };

    beforeEach(() => {
      (get as jest.Mock).mockImplementation(url => {
        if (url === USAGE_ANALYTICS_API_URL) {
          return Promise.resolve(mockAnalyticsData);
        }
        return Promise.reject();
      });
      (sendApiRequest as jest.Mock).mockImplementation(() =>
        Promise.resolve({ collect_usage: true })
      );
    });

    afterEach(() => {
      jest.clearAllMocks();
    });

    it('renders analytics title and checkbox', async () => {
      await renderAnalyticsAndWaitForLoad();

      expect(screen.getByText('Anonymous usage analytics')).toBeInTheDocument();
      expect(
        screen.getByLabelText('Help improve Hue with anonymous usage analytics.')
      ).toBeInTheDocument();
      expect(screen.getByRole('checkbox')).toBeInTheDocument();
    });

    it('fetches and displays analytics data on mount', async () => {
      await renderAnalyticsAndWaitForLoad();
      await expectCheckboxState(true);
    });

    it('checkbox reflects analytics data state when disabled', async () => {
      (get as jest.Mock).mockResolvedValue(mockAnalyticsDataDisabled);
      await renderAnalyticsAndWaitForLoad();
      await expectCheckboxState(false);
    });

    it('shows loading state during initial data fetch', () => {
      (get as jest.Mock).mockImplementation(() => new Promise(() => {})); // Never resolves
      render(<Analytics />);
      expect(screen.getAllByTestId('loading-error-wrapper__spinner')[0]).toBeInTheDocument();
    });

    it('shows error message when data fetch fails', async () => {
      const errorMessage = 'Failed to fetch analytics data';
      (get as jest.Mock).mockRejectedValue(errorMessage);
      render(<Analytics />);

      await waitFor(() => {
        expect(screen.getByTestId('loading-error-wrapper__errors')).toBeInTheDocument();
      });
    });

    it('handles checkbox toggle to enable analytics', async () => {
      (get as jest.Mock).mockResolvedValue(mockAnalyticsDataDisabled);
      await renderAnalyticsAndWaitForLoad();

      const checkbox = await expectCheckboxState(false);
      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(sendApiRequest).toHaveBeenCalledWith(
          'put',
          USAGE_ANALYTICS_API_URL,
          { collect_usage: true },
          expectedOptions
        );
      });
    });

    it('handles checkbox toggle to disable analytics', async () => {
      await renderAnalyticsAndWaitForLoad();

      const checkbox = await expectCheckboxState(true);
      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(sendApiRequest).toHaveBeenCalledWith(
          'put',
          USAGE_ANALYTICS_API_URL,
          { collect_usage: false },
          expectedOptions
        );
      });
    });

    it('disables checkbox during save operation', async () => {
      (sendApiRequest as jest.Mock).mockImplementation(() => new Promise(() => {})); // Never resolves
      await renderAnalyticsAndWaitForLoad();

      const checkbox = await expectCheckboxState(true);
      await userEvent.click(checkbox);

      await waitFor(() => {
        const currentCheckbox = getCheckboxElement();
        expect(currentCheckbox.disabled).toBe(true);
      });
    });

    it('shows loading state during save operation', async () => {
      (sendApiRequest as jest.Mock).mockImplementation(() => new Promise(() => {}));
      await renderAnalyticsAndWaitForLoad();

      const checkbox = await expectCheckboxState(true);
      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(screen.getAllByTestId('loading-error-wrapper__spinner')[0]).toBeInTheDocument();
      });
    });

    it('shows error message when save operation fails', async () => {
      const errorMessage = 'Failed to update analytics preference';
      (sendApiRequest as jest.Mock).mockRejectedValue(errorMessage);
      await renderAnalyticsAndWaitForLoad();

      const checkbox = await expectCheckboxState(true);
      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(screen.getByTestId('loading-error-wrapper__errors')).toBeInTheDocument();
      });
    });

    it('publishes success message when analytics are enabled', async () => {
      (get as jest.Mock).mockResolvedValue(mockAnalyticsDataDisabled);
      (sendApiRequest as jest.Mock).mockResolvedValue({ collect_usage: true });
      await renderAnalyticsAndWaitForLoad();

      const checkbox = await expectCheckboxState(false);
      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(huePubSub.publish).toHaveBeenCalledWith('hue.global.info', {
          message: 'Analytics have been activated.'
        });
      });
    });

    it('publishes success message when analytics are disabled', async () => {
      (sendApiRequest as jest.Mock).mockResolvedValue({ collect_usage: false });
      await renderAnalyticsAndWaitForLoad();

      const checkbox = await expectCheckboxState(true);
      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(huePubSub.publish).toHaveBeenCalledWith('hue.global.info', {
          message: 'Analytics have been deactivated.'
        });
      });
    });

    it('reloads data after successful save', async () => {
      (sendApiRequest as jest.Mock).mockResolvedValue({ collect_usage: false });
      await renderAnalyticsAndWaitForLoad();

      const checkbox = await expectCheckboxState(true);

      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(get).toHaveBeenCalledTimes(2);
        expect(get).toHaveBeenCalledWith(USAGE_ANALYTICS_API_URL, undefined, expectedFetchOptions);
      });
    });

    it('handles undefined analytics data gracefully', async () => {
      (get as jest.Mock).mockResolvedValue({});
      await renderAnalyticsAndWaitForLoad();
      await expectCheckboxState(false);
    });

    it('handles multiple error states simultaneously', async () => {
      const fetchError = 'Fetch failed';
      const saveError = 'Save failed';

      (get as jest.Mock).mockRejectedValue(fetchError);
      (sendApiRequest as jest.Mock).mockRejectedValue(saveError);

      render(<Analytics />);

      await waitFor(() => {
        expect(screen.getByTestId('loading-error-wrapper__errors')).toBeInTheDocument();
      });

      const checkbox = getCheckboxElement();
      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(screen.getByTestId('loading-error-wrapper__errors')).toBeInTheDocument();
      });
    });
  });
});
