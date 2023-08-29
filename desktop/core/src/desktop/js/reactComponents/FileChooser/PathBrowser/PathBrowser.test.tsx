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
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import PathBrowser from './PathBrowser';

const onFilepathChangeMock = jest.fn();

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

afterEach(() => {
  jest.clearAllMocks();
});

describe('Pathbrowser', () => {
  describe('Pathbrowser breadcrumbs', () => {
    test('renders the specified seperator to seperate the breadcrumbs', () => {
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'%'}
          showIcon
        />
      );
      const seperator = screen.getAllByText('%');
      expect(seperator).not.toBeNull();
    });

    test('does not render a different seperator than specified to seperate the breadcrumbs', () => {
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'%'}
          showIcon
        />
      );
      expect(screen.queryByText('/')).toBeNull();
    });

    test('renders breadcrumbs without dropdown button if there are less than or equal to 3 breadcrumbs', () => {
      const rendered = render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'/'}
          showIcon
        />
      );
      expect(rendered.queryByRole('button', { name: '..' })).toBeNull();
    });

    test('renders breadcrumbs with dropdown button if there are more than 3 breadcrumbs', () => {
      const rendered = render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          breadcrumbs={breadcrumbsTestConfig2}
          seperator={'/'}
          showIcon
        />
      );
      expect(rendered.getByRole('button', { name: '..' })).toBeVisible();
    });

    test('renders dropdown on click of dropdown button', async () => {
      const user = userEvent.setup();
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          breadcrumbs={breadcrumbsTestConfig2}
          seperator={'/'}
          showIcon
        />
      );
      //From the given testconfig: The dropdown menu would consist of menu button with label test2. 'test2' should not be visible until the dropdown button is clicked.
      expect(screen.queryByRole('button', { name: 'test2' })).not.toBeInTheDocument();
      const dropdownButton = screen.getByRole('button', { name: '..' });
      await user.click(dropdownButton);
      expect(screen.getByRole('button', { name: 'test2' })).toBeInTheDocument();
    });

    test('calls onFilepathChange on click of breadcrumb', async () => {
      const user = userEvent.setup();
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'/'}
          showIcon={false}
        />
      );
      expect(onFilepathChangeMock).not.toHaveBeenCalled();
      const breadcrumb = screen.getByRole('button', { name: 'test' });
      await user.click(breadcrumb);
      expect(onFilepathChangeMock).toHaveBeenCalled();
    });

    test('renders icon in breadcrumbs only if specified', () => {
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'/'}
          showIcon
        />
      );
      const icon = screen.getByTestId('hue-path-browser__file-system-icon');
      expect(icon).toBeVisible();
    });

    test('does not render icon in breadcrumbs if showIcon is false', () => {
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'/'}
          showIcon={false}
        />
      );
      const icon = screen.queryByTestId('hue-path-browser__file-system-icon');
      expect(icon).toBeNull();
    });
  });

  describe('Pathbrowser Input', () => {
    test('input is hidden before toggle button is clicked', () => {
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'/'}
          showIcon
        />
      );
      const input = screen.queryByDisplayValue('abfs://test/test1');
      expect(input).toBeNull();
    });

    test('renders input when toggle button is clicked', async () => {
      const user = userEvent.setup();
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          breadcrumbs={breadcrumbsTestConfig1}
          seperator={'/'}
          showIcon
        />
      );
      const toggleButton = screen.getByRole('button', {
        name: /hue-path-browser__toggle-breadcrumb-input-btn/i
      });
      await user.click(toggleButton);
      const input = screen.getByDisplayValue('abfs://test/test1');
      expect(input).toBeVisible();
    });
  });
});
