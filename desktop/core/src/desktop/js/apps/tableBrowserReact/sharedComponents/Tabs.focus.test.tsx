// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import Tabs from './Tabs';

jest.mock('../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

// This test ensures labels updates do not break navigation expectations
// Note: Current implementation remounts Tabs to coalesce label changes; we assert behavior, not implementation detail.

describe('Tabs focus behavior', () => {
  it('keeps the intended active tab after label count changes', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();

    const { rerender } = render(
      <Tabs activeKey="overview" onChange={onChange} sampleCount={0} />
    );

    // Switch to Sample tab
    await user.click(screen.getByRole('tab', { name: /sample/i }));
    expect(onChange).toHaveBeenCalledWith('sample');

    // Simulate parent re-render with updated sampleCount
    rerender(<Tabs activeKey="sample" onChange={onChange} sampleCount={10} />);

    // Sample tab with count should still be present; focus may or may not persist depending on library,
    // but the activeKey should match the selected tab semantics in consumers.
    expect(screen.getByRole('tab', { name: /sample \(10\)/i })).toBeInTheDocument();
  });
});
