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

import $ from 'jquery';
import { koSetup } from 'jest/koTestUtils';
import { NAME } from './ko.jobBrowserLinks';
import huePubSub from 'utils/huePubSub';

import { initializeMiniJobBrowser } from 'apps/jobBrowser/miniJobBrowser';
jest.mock('apps/jobBrowser/miniJobBrowser');

describe('ko.jobBrowserLinks.js', () => {
  const setup = koSetup();
  let fakeMiniPanel;

  beforeEach(() => {
    jest.spyOn($, 'post').mockImplementation(url => {
      if (url === '/jobbrowser/jobs/') {
        return $.Deferred().resolve({ jobs: [] }).promise();
      }
    });

    // This element gets created during runtime via an ajax call that gets the raw
    // html contents including scripts and styles.
    fakeMiniPanel = document.createElement('div');
    fakeMiniPanel.setAttribute('id', 'jobsPanel');
    document.body.appendChild(fakeMiniPanel);
  });

  afterEach(() => {
    jest.clearAllMocks();
    fakeMiniPanel.remove();
  });

  it('should render component', async () => {
    const element = await setup.renderComponent(NAME, {});

    expect(element.innerHTML).toMatchSnapshot();
  });

  it('should initialize the mini job browser on first open', async () => {
    window.HAS_JOB_BROWSER = true;
    window.getLastKnownConfig = () => ({});
    jest.spyOn($, 'post').mockImplementation(url => {
      if (url === '/jobbrowser/jobs/') {
        return Promise.resolve({ jobs: [] }).promise();
      }
    });
    await setup.renderComponent(NAME, {});
    expect(initializeMiniJobBrowser.mock.calls).toHaveLength(0);

    // First open
    huePubSub.publish('show.jobs.panel');
    expect(initializeMiniJobBrowser.mock.calls).toHaveLength(1);

    huePubSub.publish('hide.jobs.panel');

    // Second open
    huePubSub.publish('show.jobs.panel');
    expect(initializeMiniJobBrowser.mock.calls).toHaveLength(1);
  });
});
