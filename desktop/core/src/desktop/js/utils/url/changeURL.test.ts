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

import changeURL from './changeURL';
import { hueWindow } from 'types/types';

describe('changeURL', () => {
  const baseUrl = 'https://www.gethue.com/hue';
  const mockPushState = jest.fn();
  const mockReplaceState = jest.fn();

  beforeAll(() => {
    global.window.history.pushState = mockPushState;
    global.window.history.replaceState = mockReplaceState;
    (global.window as hueWindow).HUE_BASE_URL = baseUrl;
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should append query params to the URL with pushState', () => {
    const newURL = '/new/path';
    const params = { key1: 'value1', key2: 2 };

    changeURL(newURL, params);

    expect(mockReplaceState).not.toHaveBeenCalled();
    expect(mockPushState).toHaveBeenCalledWith(null, '', `${baseUrl}/new/path?key1=value1&key2=2`);
  });

  it('should append hash to the URL with pushState', () => {
    const newURL = '/new/path#section';
    const params = { key1: 'value1' };

    changeURL(newURL, params);

    expect(mockReplaceState).not.toHaveBeenCalled();
    expect(mockPushState).toHaveBeenCalledWith(null, '', `${baseUrl}/new/path?key1=value1#section`);
  });

  it('should handle replaceState when isReplace is true', () => {
    const newURL = '/new/path';
    const params = { key1: 'value1' };

    changeURL(newURL, params, true);

    expect(mockPushState).not.toHaveBeenCalled();
    expect(mockReplaceState).toHaveBeenCalledWith(null, '', `${baseUrl}/new/path?key1=value1`);
  });

  it('should not add the base URL if the newURL already starts with the HUE_BASE_URL', () => {
    const newURL = `${baseUrl}/new/path`;

    changeURL(newURL, { key1: 'value1' });

    expect(mockReplaceState).not.toHaveBeenCalled();
    expect(mockPushState).toHaveBeenCalledWith(null, '', `${baseUrl}/new/path?key1=value1`);
  });

  it('should handle the absence of params correctly', () => {
    const newURL = '/new/path#section';

    changeURL(newURL);

    expect(mockReplaceState).not.toHaveBeenCalled();
    expect(mockPushState).toHaveBeenCalledWith(null, '', `${baseUrl}/new/path#section`);
  });

  it('should not change the URL if the new URL is the same as the current URL with hash', () => {
    changeURL(baseUrl, {});

    expect(mockReplaceState).not.toHaveBeenCalled();
    expect(mockPushState).not.toHaveBeenCalled();
  });
});
