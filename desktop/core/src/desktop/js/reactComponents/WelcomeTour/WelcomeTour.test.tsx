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
import { act, render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import huePubSub from 'utils/huePubSub';

import WelcomeTour from './WelcomeTour';

describe('WelcomeTour', () => {
  test('it should show the welcome tour on huePubSub event', async () => {
    render(<WelcomeTour />);
    expect(screen.queryByText(/Welcome to Hue 4!/)).not.toBeInTheDocument();

    await act(async () => {
      huePubSub.publish('show.welcome.tour');
      await new Promise(process.nextTick);
    });

    expect(screen.queryByText(/Welcome to Hue 4!/)).toBeInTheDocument();
  });
});
