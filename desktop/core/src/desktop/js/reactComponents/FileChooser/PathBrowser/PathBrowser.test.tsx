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
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import PathBrowser from './PathBrowser';
import { debug } from 'webpack';

const handleFilePathChangeMock = jest.fn();

const breadcrumbsTestConfig1 = [
  {
    url: 'abfs://',
    label: 'abfs://'
  },
  {
    url: 'abfs://test',
    label: 'test'
  },
  {
    url: 'abfs://test/test1',
    label: 'test1'
  }
];

const breadcrumbsTestConfig2 = [
  {
    url: 'abfs://',
    label: 'abfs://'
  },
  {
    url: 'abfs://test',
    label: 'test'
  },
  {
    url: 'abfs://test/test1',
    label: 'test1'
  },
  {
    url: 'abfs://test/test1/test2',
    label: 'test2'
  },
  {
    url: 'abfs://test/test1/test2/a very very very long test label',
    label: 'a very very very long test label'
  },
  {
    url: 'abfs://test/test1/test2/a very very very long test label/a very very very long test label 1',
    label: 'a very very very long test label 1'
  },
  {
    url: 'abfs://test/test1/test2/a very very very long test label/a very very very long test label 1/a very very very long test label 2',
    label: 'a very very very long test label 2'
  }
];

describe('Pathbrowser', () => {
  describe('Pathbrowser breadcrumbs', () => {
    test('renders the specified seperator to seperate the breadcrumbs', () => {
      render(
        <PathBrowser
          handleFilePathChange={handleFilePathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'%'}
          showIcon
        />
      );
      const seperator = screen.getAllByTestId('hue-path-browser-breadcrumb-seperator');
      expect(within(seperator[0]).getByText('%')).toBeVisible();
    });

    test('renders breadcrumbs without dropdown if there are less than or equal to 3 breadcrumbs', () => {
      const rendered = render(
        <PathBrowser
          handleFilePathChange={handleFilePathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'/'}
          showIcon
        />
      );
      expect(rendered.queryByTestId('hue-path-browser-dropdown-btn')).toBeNull();
    });

    test('renders breadcrumbs with dropdown if there are more than 3 breadcrumbs', () => {
      const rendered = render(
        <PathBrowser
          handleFilePathChange={handleFilePathChangeMock}
          breadcrumbs={breadcrumbsTestConfig2}
          seperator={'/'}
          showIcon
        />
      );
      expect(rendered.queryByTestId('hue-path-browser-dropdown-btn')).toBeVisible();
    });

    test('renders dropdown on click of dropdown button', async () => {
      const user = userEvent.setup();
      render(
        <PathBrowser
          handleFilePathChange={handleFilePathChangeMock}
          breadcrumbs={breadcrumbsTestConfig2}
          seperator={'/'}
          showIcon
        />
      );

      expect(
        screen.queryByTestId('hue-path-browser__overflowing-label-menu')
      ).not.toBeInTheDocument();

      const dropdownButton = screen.getByTestId('hue-path-browser-dropdown-btn');
      await user.click(dropdownButton);

      expect(
        screen.queryAllByTestId('hue-path-browser__overflowing-label-menu')[0]
      ).toBeInTheDocument();
      const dropdown = screen.queryAllByTestId('hue-path-browser__overflowing-label-menu');
      //Checking for 2nd menu item to be present
      expect(dropdown[2]).toHaveTextContent('test2');
    });

    test('renders icon in breadcrumbs only if specified', () => {
      render(
        <PathBrowser
          handleFilePathChange={handleFilePathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'%'}
          showIcon
        />
      );
      const icon = screen.getByTestId('hue-path-browser-icon');
      expect(icon).toBeVisible();
    });

    test('does not render icon in breadcrumbs if showIcon is false', () => {
      render(
        <PathBrowser
          handleFilePathChange={handleFilePathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'%'}
          showIcon={false}
        />
      );
      const icon = screen.getByTestId('hue-path-browser-icon');
      //display: none is not recognised to use toBeVisible.
      expect(icon).toHaveClass('hide-hue-filesystem__icon');
    });

    test('calls handleFilePathChange on click of breadcrumb', async () => {
      const user = userEvent.setup();
      render(
        <PathBrowser
          handleFilePathChange={handleFilePathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'%'}
          showIcon={false}
        />
      );
      expect(handleFilePathChangeMock).not.toHaveBeenCalled();
      const breadcrumb = screen.queryAllByTestId(
        'hue-path-browser__overflowing-label-breadcrumb'
      )[1];
      await user.click(breadcrumb);
      expect(handleFilePathChangeMock).toHaveBeenCalled();
    });
  });

  describe('Pathbrowser Input', () => {
    test('renders input when toggle button is clicked', async () => {
      const user = userEvent.setup();
      render(
        <PathBrowser
          handleFilePathChange={handleFilePathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'%'}
          showIcon
        />
      );
      const toggleButton = screen.getByTestId('hue-path-browser-toggle-input-btn');
      await user.click(toggleButton);
      const input = screen.getByTestId('hue-path-browser-input');
      expect(input).toBeVisible();
    });
  });
});
