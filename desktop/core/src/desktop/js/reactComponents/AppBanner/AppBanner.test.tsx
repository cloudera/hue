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
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import AppBanner from './AppBanner';
import { CancellablePromise } from '../../api/cancellablePromise';
import * as ApiUtils from '../../api/utils';

describe('AppBanner', () => {
  let apiMock;

  const setupMock = (configured?: string, system?: string) => {
    apiMock = jest
      .spyOn<ApiUtils, ApiUtils['get']>(ApiUtils, 'get')
      .mockReturnValue(CancellablePromise.resolve({ configured, system }));
  };

  afterEach(() => {
    apiMock?.mockClear();
  });

  test('it should show a configured banner', async () => {
    const configuredBanner = '<div>Configured text <a href="some">Link</a></div>';
    setupMock(configuredBanner);

    render(<AppBanner />);

    expect((await screen.findByText(/Configured/))?.outerHTML).toEqual(configuredBanner);
  });

  test('it should show a sanitized configured banner', async () => {
    const configuredBanner =
      '<div>Configured text <a href="some">Link</a><script>alert("xss");</script></div>';
    const expectedBanner = '<div>Configured text <a href="some">Link</a></div>';
    setupMock(configuredBanner);

    render(<AppBanner />);

    expect((await screen.findByText(/Configured/))?.outerHTML).toEqual(expectedBanner);
  });

  test('it should show a configured banner with sanitized styles', async () => {
    const configuredBanner =
      '<div style="color: #aabbcc; width: expression(alert(\'XSS\'));font-size:1px;">Configured text</div>';
    const expectedBanner = '<div style="color:#aabbcc;font-size:1px">Configured text</div>';
    setupMock(configuredBanner);

    render(<AppBanner />);

    expect((await screen.findByText(/Configured/))?.outerHTML).toEqual(expectedBanner);
  });

  test('it should show a system banner', async () => {
    const systemBanner = '<div>System text</div>';
    setupMock(undefined, systemBanner);

    render(<AppBanner />);

    expect((await screen.findByText(/System/))?.outerHTML).toEqual(systemBanner);
  });

  test('it should show a system banner instead of configured if both are present', async () => {
    const configuredBanner = '<div>Configured text <a href="some">Link</a></div>';
    const systemBanner = '<div>System text</div>';
    setupMock(configuredBanner, systemBanner);

    render(<AppBanner />);

    expect(await screen.findByText(/System/)).toBeInTheDocument();
    expect(screen.queryByText(/Configured/)).not.toBeInTheDocument();
  });
});
