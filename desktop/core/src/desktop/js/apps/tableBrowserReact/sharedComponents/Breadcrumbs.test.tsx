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

import Breadcrumbs from './Breadcrumbs';
import { NavigationProvider, type NavigationAPI } from './NavigationContext';

jest.mock('../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

describe('Breadcrumbs', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'location', {
      value: { pathname: '/hue/tablebrowser' },
      writable: true
    });
  });

  it('renders and calls navigation callbacks', async () => {
    const user = userEvent.setup();
    const onClickDataSources = jest.fn();
    const onClickDatabases = jest.fn();
    const onClickDatabase = jest.fn();
    const onClickTable = jest.fn();

    render(
      <Breadcrumbs
        sourceType="hive"
        database="default"
        table="customers"
        onClickDataSources={onClickDataSources}
        onClickDatabases={onClickDatabases}
        onClickDatabase={onClickDatabase}
        onClickTable={onClickTable}
      />
    );

    // Data sources crumb
    await user.click(screen.getByRole('link', { name: 'Data sources' }));
    expect(onClickDataSources).toHaveBeenCalledTimes(1);

    // Source crumb
    await user.click(screen.getByRole('link', { name: 'HIVE' }));
    expect(onClickDatabases).toHaveBeenCalledTimes(1);

    // Database crumb
    await user.click(screen.getByRole('link', { name: 'default' }));
    expect(onClickDatabase).toHaveBeenCalledWith('default');

    // Table crumb (when table is active, it's a span; with column it is a link). Force link by passing column.
  });

  it('uses NavigationContext when overrides are not provided', async () => {
    const user = userEvent.setup();

    const nav: NavigationAPI = {
      navigateToSources: jest.fn(),
      navigateToSource: jest.fn(),
      navigateToDatabase: jest.fn(),
      navigateToTable: jest.fn(),
      navigateToColumn: jest.fn(),
      navigateToField: jest.fn()
    };

    render(
      <NavigationProvider value={nav}>
        <Breadcrumbs
          sourceType="hive"
          database="default"
          table="customers"
          column="id"
          fields={['a', 'b']}
        />
      </NavigationProvider>
    );

    // Data sources crumb
    await user.click(screen.getByRole('link', { name: 'Data sources' }));
    expect(nav.navigateToSources).toHaveBeenCalledTimes(1);

    // Source crumb (HIVE)
    await user.click(screen.getByRole('link', { name: 'HIVE' }));
    expect(nav.navigateToSource).toHaveBeenCalledWith('hive');

    // Database crumb
    await user.click(screen.getByRole('link', { name: 'default' }));
    expect(nav.navigateToDatabase).toHaveBeenCalledWith('default');

    // Table crumb (when column exists, table is a link)
    await user.click(screen.getByRole('link', { name: 'customers' }));
    expect(nav.navigateToTable).toHaveBeenCalledWith('default', 'customers');

    // Column crumb is current page when fields exist, so only table is a link
    expect(screen.getByText('id')).toHaveAttribute('aria-current', 'page');

    // Field crumb (first field is link, last is current)
    await user.click(screen.getByRole('link', { name: 'a' }));
    expect(nav.navigateToField).toHaveBeenCalledWith('default', 'customers', 'id', ['a']);
  });

  it('shows current item with aria-current', () => {
    render(<Breadcrumbs sourceType="impala" database="sales" table="orders" />);

    expect(screen.getByText('orders')).toHaveAttribute('aria-current', 'page');
  });
});
