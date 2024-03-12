/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import React from 'react';
import { render, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import AiAssistToolbarHistory from './AiAssistToolbarHistory'; // Adjust the import path according to your file structure

// Mock data for history items
const historyItems = [
  { date: Date.now(), value: 'First Entry' },
  { date: Date.now() - 10000, value: 'second entry' },
  { date: Date.now() - 20000, value: 'MixedCASE Entry' },
  { date: Date.now() - 30000, value: 'Last item' }
];

describe('AiAssistToolbarHistory', () => {
  const originalScrollIntoView = window.HTMLElement.prototype.scrollIntoView;

  beforeAll(() => {
    window.HTMLElement.prototype.scrollIntoView = jest.fn();
  });

  afterAll(() => {
    window.HTMLElement.prototype.scrollIntoView = originalScrollIntoView;
  });

  test('renders all history items preserving case', async () => {
    const { getByText } = render(
      <AiAssistToolbarHistory
        items={historyItems}
        searchValue=""
        onSelect={jest.fn()}
        onHide={jest.fn()}
        onToggleAutoShow={jest.fn()}
        show={true}
        autoShow={false}
        position={{ top: 0, left: 0 }}
        width={300}
      />
    );

    expect(getByText('First Entry')).toBeInTheDocument();
    expect(getByText('second entry')).toBeInTheDocument();
    expect(getByText('MixedCASE Entry')).toBeInTheDocument();
    expect(getByText('Last item')).toBeInTheDocument();
  });

  test('filters and displays history items preserving case sensitivity', async () => {
    const { getByText, queryByText } = render(
      <AiAssistToolbarHistory
        items={historyItems}
        searchValue="Entry"
        onSelect={jest.fn()}
        onHide={jest.fn()}
        onToggleAutoShow={jest.fn()}
        show={true}
        autoShow={false}
        position={{ top: 0, left: 0 }}
        width={300}
      />
    );

    expect(getByText((_, element) => element?.textContent === 'First Entry')).toBeInTheDocument();
    expect(getByText((_, element) => element?.textContent === 'second entry')).toBeInTheDocument();
    expect(
      getByText((_, element) => element?.textContent === 'MixedCASE Entry')
    ).toBeInTheDocument();
    expect(queryByText((_, element) => element?.textContent === 'Last item')).toBeNull();
  });

  test('toggles visibility based on the show prop', async () => {
    const { rerender, queryByText } = render(
      <AiAssistToolbarHistory
        items={historyItems}
        searchValue=""
        onSelect={jest.fn()}
        onHide={jest.fn()}
        onToggleAutoShow={jest.fn()}
        show={false}
        autoShow={false}
        position={{ top: 0, left: 0 }}
        width={300}
      />
    );

    expect(queryByText('First Entry')).toBeNull();

    // Rerender with the `show` prop set to true
    rerender(
      <AiAssistToolbarHistory
        items={historyItems}
        searchValue=""
        onSelect={jest.fn()}
        onHide={jest.fn()}
        onToggleAutoShow={jest.fn()}
        show={true}
        autoShow={false}
        position={{ top: 0, left: 0 }}
        width={300}
      />
    );

    expect(queryByText('First Entry')).toBeInTheDocument();
  });

  test('selects a history item on click', async () => {
    const user = userEvent.setup();
    const onSelectMock = jest.fn();
    const { getByText } = render(
      <AiAssistToolbarHistory
        items={historyItems}
        searchValue=""
        onSelect={onSelectMock}
        onHide={jest.fn()}
        onToggleAutoShow={jest.fn()}
        show={true}
        autoShow={false}
        position={{ top: 0, left: 0 }}
        width={300}
      />
    );

    await user.click(getByText('First Entry'));

    expect(onSelectMock).toHaveBeenCalledWith(expect.objectContaining({ value: 'First Entry' }));
  });

  test('navigates history items with keyboard and selects an item', async () => {
    const user = userEvent.setup();
    const onSelectMock = jest.fn();

    render(
      <AiAssistToolbarHistory
        items={historyItems}
        searchValue=""
        onSelect={onSelectMock}
        onHide={jest.fn()}
        onToggleAutoShow={jest.fn()}
        show={true}
        autoShow={false}
        position={{ top: 0, left: 0 }}
        width={300}
      />
    );

    const menu = document.querySelector('[role="menu"]') as HTMLElement;
    act(() => {
      menu?.focus(); // Directly focus to bypass any non-focusable elements
    });

    expect(document.activeElement).toEqual(menu);
    await user.keyboard('{ArrowDown}');
    await user.keyboard('{Enter}');

    expect(onSelectMock).toHaveBeenCalledWith(expect.objectContaining(historyItems[1]));
  });
  test('highlights search terms in history items', async () => {
    const onSelectMock = jest.fn();
    const { getByText, rerender } = render(
      <AiAssistToolbarHistory
        items={historyItems}
        searchValue=""
        onSelect={onSelectMock}
        onHide={jest.fn()}
        onToggleAutoShow={jest.fn()}
        show={true}
        autoShow={false}
        position={{ top: 0, left: 0 }}
        width={300}
      />
    );

    // Update the component with a search value
    rerender(
      <AiAssistToolbarHistory
        items={historyItems}
        searchValue="First"
        onSelect={onSelectMock}
        onHide={jest.fn()}
        onToggleAutoShow={jest.fn()}
        show={true}
        autoShow={false}
        position={{ top: 0, left: 0 }}
        width={300}
      />
    );

    // Check if the search term is highlighted in the history items
    const highlightedText = getByText('First');
    expect(highlightedText).toHaveClass('hue-ai-assist-toolbar-history__item-highlight');
  });
});
