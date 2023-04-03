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

import ImportIcon from '../../components/icons/ImportIcon';

import Toolbar, { ToolbarButton, ToolbarDivider } from './Toolbar';

describe('Toolbar', () => {
  test('renders any content', () => {
    render(<Toolbar content={() => <div>custom content</div>} />);
    expect(screen.getByText('custom content')).toBeVisible();
  });

  test('has default test-id "hue-toolbar"', () => {
    render(<Toolbar content={() => <div></div>} />);
    expect(screen.getByTestId('hue-toolbar')).toBeVisible();
  });

  test('offers custom test-id', () => {
    render(<Toolbar testId="custom-test-id" content={() => <div></div>} />);
    expect(screen.getByTestId('custom-test-id')).toBeVisible();
  });

  test('can have custom classname', () => {
    render(<Toolbar className="test-class" content={() => <div></div>} />);
    expect(screen.getByRole('list')).toHaveClass('test-class');
  });

  test('has default size of medium', () => {
    render(<Toolbar content={() => <div></div>} />);
    expect(screen.getByRole('list')).toHaveClass('hue-toolbar--medium');
  });

  test('can have be of size large', () => {
    render(<Toolbar size="large" content={() => <div></div>} />);
    expect(screen.getByRole('list')).toHaveClass('hue-toolbar--large');
  });

  test('can have be of size small', () => {
    render(<Toolbar size="small" content={() => <div></div>} />);
    expect(screen.getByRole('list')).toHaveClass('hue-toolbar--small');
  });

  describe('ToolbarButton', () => {
    test('renders a button wrapped in a list element to match the parent menu tag', () => {
      render(<Toolbar content={() => <ToolbarButton />} />);
      expect(screen.getByRole('button').closest('li')).toBeVisible();
    });

    test('renders a button name', () => {
      render(<Toolbar content={() => <ToolbarButton> testbutton </ToolbarButton>} />);
      expect(screen.getByRole('button', { name: 'testbutton' })).toBeVisible();
    });

    test('has default test-id "hue-toolbar-button" on wrapping li element', () => {
      render(<Toolbar content={() => <ToolbarButton />} />);
      expect(screen.getByTestId('hue-toolbar-button')).toBeVisible();
    });

    test('offers custom test-id on wrapping li element', () => {
      render(<Toolbar content={() => <ToolbarButton testId="button-test-id" />} />);
      expect(screen.getByTestId('button-test-id')).toBeVisible();
    });

    test('default test-id on button element', () => {
      render(<Toolbar content={() => <ToolbarButton />} />);
      expect(screen.getByTestId('hue-toolbar-button-btn')).toBeVisible();
    });

    test('offers custom test-id on button element', () => {
      render(<Toolbar content={() => <ToolbarButton testId="button-test-id" />} />);
      expect(screen.getByTestId('button-test-id-btn')).toBeVisible();
    });

    test('can have custom classname on wrapping li element', () => {
      render(<Toolbar content={() => <ToolbarButton className="test-button-class" />} />);
      expect(screen.getByRole('listitem')).toHaveClass('test-button-class');
    });

    test('can render multiple buttons', () => {
      render(
        <Toolbar
          content={() => (
            <>
              <ToolbarButton />
              <ToolbarButton />
              <ToolbarButton />
            </>
          )}
        />
      );
      expect(screen.getAllByRole('button')).toHaveLength(3);
    });

    test('supports icon on the left', () => {
      render(
        <Toolbar
          content={() => (
            <ToolbarButton iconPosition="left" icon={<ImportIcon data-testid="test-icon" />}>
              test-label
            </ToolbarButton>
          )}
        />
      );
      const buttonContentDiv = screen.getByRole('button').firstElementChild;
      const testIcon = screen.getByTestId('test-icon');
      const leftElement = buttonContentDiv?.childNodes[0];
      const rightElement = buttonContentDiv?.childNodes[1];
      expect(leftElement).toEqual(testIcon);
      expect(rightElement).toHaveTextContent('test-label');
    });

    test('supports icon on the right', () => {
      render(
        <Toolbar
          content={() => (
            <ToolbarButton iconPosition="right" icon={<ImportIcon data-testid="test-icon" />}>
              test-label
            </ToolbarButton>
          )}
        />
      );
      const buttonContentDiv = screen.getByRole('button').firstElementChild;
      const testIcon = screen.getByTestId('test-icon');
      const leftElement = buttonContentDiv?.childNodes[0];
      const rightElement = buttonContentDiv?.childNodes[1];
      expect(leftElement).toHaveTextContent('test-label');
      expect(rightElement).toEqual(testIcon);
    });

    test('supports aria-label for icon only button', () => {
      render(
        <Toolbar
          content={() => <ToolbarButton aria-label="test-aria-label" icon={<ImportIcon />} />}
        />
      );
      const button = screen.getByRole('button', { name: 'test-aria-label' });
      expect(button.getAttribute('aria-label')).toEqual('test-aria-label');
    });

    test('supports title for icon only button', () => {
      render(
        <Toolbar content={() => <ToolbarButton title="test-title" icon={<ImportIcon />} />} />
      );

      const button = screen.getByRole('button', { name: 'test-title' });
      expect(button.getAttribute('title')).toEqual('test-title');
    });

    test('accepts JSX element as child', () => {
      render(
        <Toolbar
          content={() => (
            <ToolbarButton aria-label="test-aria-label">
              <div>test-jsx-child</div>
            </ToolbarButton>
          )}
        />
      );

      expect(screen.getByText('test-jsx-child')).toBeVisible();
    });

    test('can be disabled', () => {
      const { rerender } = render(<Toolbar content={() => <ToolbarButton disabled />} />);
      expect(screen.getByRole('button')).toBeDisabled();

      rerender(<Toolbar content={() => <ToolbarButton />} />);
      expect(screen.getByRole('button')).not.toBeDisabled();
    });

    test('can be turned into a href link with target', () => {
      render(
        <Toolbar
          content={() => (
            <ToolbarButton href="test-url" target="blank">
              anchor-link-button
            </ToolbarButton>
          )}
        />
      );
      const btn = screen.getByRole('link', { name: 'anchor-link-button' });
      expect(btn.getAttribute('href')).toEqual('test-url');
      expect(btn.getAttribute('target')).toEqual('blank');
    });

    test('calls provided onClick callback when clicked', async () => {
      const user = userEvent.setup();
      const callback = jest.fn();
      render(<Toolbar content={() => <ToolbarButton onClick={callback} />} />);
      const testButtton = screen.getByRole('button');
      expect(callback).not.toHaveBeenCalled();
      await user.click(testButtton);
      expect(callback).toHaveBeenCalled();
    });
  });

  describe('ToolbarDivider', () => {
    test('renders a vertical divider wrapped in a li tag', () => {
      render(<Toolbar content={() => <ToolbarDivider />} />);
      expect(screen.getByRole('separator')).toHaveClass('ant-divider-vertical');
      expect(screen.getByRole('separator').closest('li')).toBeDefined();
    });

    test('wrapping list item has default test id', () => {
      render(<Toolbar content={() => <ToolbarDivider />} />);
      expect(screen.getByTestId('hue-toolbar-divider')).toBeVisible();
    });

    test('wrapping list item supports custom test id', () => {
      render(<Toolbar content={() => <ToolbarDivider testId="custom-test-id" />} />);
      expect(screen.getByTestId('custom-test-id')).toBeVisible();
    });
  });
});
