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
import { act, getByRole, render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import huePubSub from '../../utils/huePubSub';

import AlertComponent from './AlertComponent';

describe('AlertComponent', () => {
  test('it should show a global error message', async () => {
    render(<AlertComponent />);
    expect(screen.queryAllByRole('alert')).toHaveLength(0);

    act(() => huePubSub.publish('hue.global.error', { message: 'Some error' }));

    const alerts = screen.queryAllByRole('alert');
    expect(alerts).toHaveLength(1);
    expect(alerts[0]).toHaveTextContent('Some error');
  });

  test('it should show multiple global error messages', async () => {
    render(<AlertComponent />);
    expect(screen.queryAllByRole('alert')).toHaveLength(0);

    act(() => huePubSub.publish('hue.global.error', { message: 'Error 1' }));
    act(() => huePubSub.publish('hue.global.error', { message: 'Error 2' }));

    const alerts = screen.queryAllByRole('alert');
    expect(alerts).toHaveLength(2);
    expect(alerts[0]).toHaveTextContent('Error 1');
    expect(alerts[1]).toHaveTextContent('Error 2');
  });

  test("it shouldn't show empty error messages", async () => {
    render(<AlertComponent />);
    expect(screen.queryAllByRole('alert')).toHaveLength(0);

    act(() => huePubSub.publish('hue.global.error', { message: '' }));

    expect(screen.queryAllByRole('alert')).toHaveLength(0);
  });

  test('it should show unique error messages', async () => {
    render(<AlertComponent />);
    expect(screen.queryAllByRole('alert')).toHaveLength(0);

    act(() => huePubSub.publish('hue.global.error', { message: 'Error 1' }));
    act(() => huePubSub.publish('hue.global.error', { message: 'Error 2' }));
    act(() => huePubSub.publish('hue.global.error', { message: 'Error 1' }));

    const alerts = screen.queryAllByRole('alert');
    expect(alerts).toHaveLength(2);
    expect(alerts[0]).toHaveTextContent('Error 1');
    expect(alerts[1]).toHaveTextContent('Error 2');
  });

  test('alerts should be closable', async () => {
    const user = userEvent.setup();
    render(<AlertComponent />);
    expect(screen.queryAllByRole('alert')).toHaveLength(0);
    act(() => huePubSub.publish('hue.global.error', { message: 'Error 1' }));
    act(() => huePubSub.publish('hue.global.error', { message: 'Error 2' }));
    act(() => huePubSub.publish('hue.global.error', { message: 'Error 3' }));

    // Closing "Error 2"
    const initialAlerts = screen.queryAllByRole('alert');
    expect(initialAlerts).toHaveLength(3);
    const closeButton = getByRole(initialAlerts[1], 'button');
    await user.click(closeButton);

    const alertsAfterClosing = screen.queryAllByRole('alert');
    expect(alertsAfterClosing).toHaveLength(2);
    expect(alertsAfterClosing[0]).toHaveTextContent('Error 1');
    expect(alertsAfterClosing[1]).toHaveTextContent('Error 3');
  });

  test('info alerts should close automatically after 3 seconds', async () => {
    jest.useFakeTimers();
    render(<AlertComponent />);
    expect(screen.queryAllByRole('alert')).toHaveLength(0);
    act(() => huePubSub.publish('hue.global.info', { message: 'info' }));
    expect(screen.queryAllByRole('alert')).toHaveLength(1);

    //It should still be open after 2 seconds
    act(() => {
      jest.advanceTimersByTime(2000);
    });
    expect(screen.queryAllByRole('alert')).toHaveLength(1);

    //After 3.1 seconds, it should really be closed
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    expect(screen.queryAllByRole('alert')).toHaveLength(0);

    jest.useRealTimers();
  });
});
