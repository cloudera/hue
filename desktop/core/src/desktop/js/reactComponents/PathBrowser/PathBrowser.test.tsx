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
import { act } from 'react-dom/test-utils';

import PathBrowser from './PathBrowser';

afterEach(() => {
  jest.clearAllMocks();
});

describe('Pathbrowser', () => {
  const onFilepathChangeMock = jest.fn();
  const mockFilePath = 'abfs://test/folder';
  const mockLongFilePath = 'abfs://path/to/nested1/nested2/nested3/folder';
  describe('Pathbrowser breadcrumbs', () => {
    it('should render the specified separator to separate the breadcrumbs', () => {
      render(
        <PathBrowser
          filePath={mockFilePath}
          onFilepathChange={onFilepathChangeMock}
          separator={'%'}
          showIcon
        />
      );
      const separator = screen.getAllByText('%');
      expect(separator).not.toBeNull();
    });

    it('should not render a different separator than specified to separate the breadcrumbs', () => {
      render(
        <PathBrowser
          testId="pathbroswer"
          filePath={mockFilePath}
          onFilepathChange={onFilepathChangeMock}
          separator={'%'}
          showIcon
        />
      );
      screen
        .getAllByTestId('pathbroswer-breadcrumb-separator')
        .slice(1)
        .forEach(element => {
          expect(element).toBeVisible();
          expect(element).toHaveTextContent('%');
        });
    });

    it('should render breadcrumbs without dropdown button if there are less than or equal to 3 breadcrumbs', () => {
      const rendered = render(
        <PathBrowser
          filePath={mockFilePath}
          onFilepathChange={onFilepathChangeMock}
          separator="/"
          showIcon
        />
      );
      expect(rendered.queryByRole('button', { name: '..' })).toBeNull();
    });

    it('should render breadcrumbs with dropdown button if there are more than 3 breadcrumbs', () => {
      const rendered = render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          filePath={mockLongFilePath}
          separator="/"
          showIcon
        />
      );
      expect(rendered.getByRole('button', { name: '..' })).toBeVisible();
    });

    it('should render dropdown on click of dropdown button', async () => {
      const user = userEvent.setup();
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          filePath={mockLongFilePath}
          separator="/"
          showIcon
        />
      );
      //From the given testconfig: The dropdown menu would consist of menu button with label test2. 'test2' should not be visible until the dropdown button is clicked.
      expect(screen.queryByRole('menuitem', { name: 'nested3' })).not.toBeInTheDocument();
      const dropdownButton = await screen.getByRole('button', { name: '..' });
      await user.click(dropdownButton);
      expect(screen.getByRole('menuitem', { name: 'nested2' })).toBeInTheDocument();
    });

    it('should calls onFilepathChange on click of breadcrumb', async () => {
      const user = userEvent.setup();
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          filePath={mockFilePath}
          separator="/"
          showIcon={false}
        />
      );
      expect(onFilepathChangeMock).not.toHaveBeenCalled();
      const breadcrumb = screen.getByRole('button', { name: 'test' });
      await user.click(breadcrumb);
      expect(onFilepathChangeMock).toHaveBeenCalled();
    });

    it('should render icon in breadcrumbs only if specified', () => {
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          filePath={mockFilePath}
          separator="/"
          showIcon
        />
      );
      const icon = screen.getByTestId('hue-path-browser__file-system-icon');
      expect(icon).toBeVisible();
    });

    it('should not render icon in breadcrumbs if showIcon is false', () => {
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          filePath={mockFilePath}
          separator="/"
          showIcon={false}
        />
      );
      const icon = screen.queryByTestId('hue-path-browser__file-system-icon');
      expect(icon).toBeNull();
    });
  });

  describe('Pathbrowser Input', () => {
    it('should input is hidden before toggle button is clicked', () => {
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          filePath={mockFilePath}
          separator="/"
          showIcon
        />
      );
      const input = screen.queryByDisplayValue(mockFilePath);
      expect(input).toBeNull();
    });

    it('should show input when edit path button is clicked', async () => {
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          filePath={mockFilePath}
          separator="/"
          showIcon
        />
      );
      let input = screen.queryByDisplayValue(mockFilePath);
      expect(input).toBeNull();
      const editPathButton = screen.getByTestId('hue-path-browser__edit-path-btn');
      await userEvent.click(editPathButton);
      input = screen.getByDisplayValue(mockFilePath);
      expect(input).not.toBeNull();
    });
  });

  describe('Pathbrowser Copy Path Button', () => {
    it('should show green tick icon for 2 seconds after copying path', async () => {
      const user = userEvent.setup();
      render(
        <PathBrowser
          onFilepathChange={onFilepathChangeMock}
          filePath={mockFilePath}
          separator="/"
          showIcon
        />
      );

      const copyPathButton = screen.getByRole('button', { name: 'Copy Path' });
      expect(copyPathButton).toBeInTheDocument();
      expect(screen.queryByTestId('hue-path-browser__status-success-icon')).not.toBeInTheDocument();
      expect(screen.getByTestId('hue-path-browser__path-copy-icon')).toBeInTheDocument();

      await user.click(copyPathButton);

      expect(screen.getByTitle('Copied!')).toBeInTheDocument();

      expect(screen.getByTestId('hue-path-browser__status-success-icon')).toBeInTheDocument();
      expect(screen.queryByTestId('hue-path-browser__path-copy-icon')).not.toBeInTheDocument();

      // Wait for 2 seconds and check if the green tick icon disappears
      await act(() => new Promise(resolve => setTimeout(resolve, 2000)));
      expect(screen.queryByTestId('hue-path-browser__status-success-icon')).not.toBeInTheDocument();
      expect(screen.getByTestId('hue-path-browser__path-copy-icon')).toBeInTheDocument();
    });
  });
});
