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

import { renderHook, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import huePubSub from '../../huePubSub';
import { useCurrentApp } from './useCurrentApp';

describe('useCurrentApp', () => {
  beforeEach(() => {
    huePubSub.removeAll('set.current.app.name');
    huePubSub.removeAll('set.current.app.name');
  });

  afterEach(() => {
    huePubSub.removeAll('set.current.app.name');
    huePubSub.removeAll('set.current.app.name');
  });

  it('should return undefined initially when no app is set', () => {
    const { result } = renderHook(useCurrentApp);

    expect(result.current.currentApp).toBeUndefined();
    expect(result.current.isApp('storagebrowser')).toBe(false);
  });

  it('should update when app name is published', () => {
    const { result } = renderHook(useCurrentApp);

    act(() => {
      huePubSub.publish('set.current.app.name', 'storagebrowser');
    });

    expect(result.current.currentApp).toBe('storagebrowser');
    expect(result.current.isApp('storagebrowser')).toBe(true);
    expect(result.current.isApp('editor')).toBe(false);
  });

  it('should handle app name changes', () => {
    const { result } = renderHook(useCurrentApp);

    act(() => {
      huePubSub.publish('set.current.app.name', 'editor');
    });

    expect(result.current.currentApp).toBe('editor');
    expect(result.current.isApp('editor')).toBe(true);

    act(() => {
      huePubSub.publish('set.current.app.name', 'dashboard');
    });

    expect(result.current.currentApp).toBe('dashboard');
    expect(result.current.isApp('dashboard')).toBe(true);
    expect(result.current.isApp('editor')).toBe(false);
  });

  it('should request current app name on mount', () => {
    const subscription = huePubSub.subscribe(
      'get.current.app.name',
      (callback: (appName: string) => void) => {
        callback('metastore');
      }
    );

    const { result } = renderHook(useCurrentApp);

    expect(result.current.currentApp).toBe('metastore');

    subscription.remove();
  });
});
