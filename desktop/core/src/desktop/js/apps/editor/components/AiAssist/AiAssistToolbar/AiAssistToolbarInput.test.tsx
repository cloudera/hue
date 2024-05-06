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
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';

import AiAssistToolbarInput from './AiAssistToolbarInput';
import huePubSub from '../../../../../utils/huePubSub';

jest.mock('utils/huePubSub', () => ({
  subscribe: jest.fn(() => ({
    remove: jest.fn()
  })),
  publish: jest.fn(() => ({
    remove: jest.fn()
  }))
}));

describe('AiAssistToolbarInput', () => {
  let testProps;

  beforeAll(() => {
    global.ResizeObserver = class ResizeObserver {
      observe = jest.fn();
      unobserve = jest.fn();
      disconnect = jest.fn();
    };
  });

  beforeEach(() => {
    testProps = {
      isAnimating: false,
      isExpanded: true,
      isLoading: false,
      placeholder: '',
      prefill: '',
      onSubmit: jest.fn(),
      onCancel: jest.fn(),
      onInputChanged: jest.fn(),
      onAnimationEnded: jest.fn(),
      value: ''
    };
  });

  it('should render without errors', () => {
    const { getByRole } = render(<AiAssistToolbarInput {...testProps} />);

    expect(
      getByRole('textbox', { name: 'Press down arrow to select from history' })
    ).toBeInstanceOf(HTMLTextAreaElement);
  });

  it('should only render submit button if input contains more than 3 letters', async () => {
    const { queryByRole, rerender } = render(<AiAssistToolbarInput {...testProps} value="abcd" />);

    const btnName = 'Press enter or click here to execute';

    expect(queryByRole('button', { name: btnName })).toBeInTheDocument();

    rerender(<AiAssistToolbarInput {...testProps} value="abc" />);
    expect(queryByRole('button', { name: btnName })).not.toBeInTheDocument();
  });

  it('should call onSubmit when clicking the execute button', async () => {
    const user = userEvent.setup();
    const onSubmitMock = jest.fn();
    const { getByRole } = render(
      <AiAssistToolbarInput {...testProps} value="abcd" onSubmit={onSubmitMock} />
    );

    expect(onSubmitMock).not.toHaveBeenCalled();
    const btnName = 'Press enter or click here to execute';
    const btn = getByRole('button', { name: btnName });
    await user.click(btn);
    expect(onSubmitMock).toHaveBeenCalled();
  });

  it('should call onSubmit when pressing the enter key with more then 4 non digit input', async () => {
    const user = userEvent.setup();
    const onSubmitMock = jest.fn();
    const { getByRole } = render(
      // We include a non-ascii character to test the regex
      <AiAssistToolbarInput {...testProps} value="abc好" onSubmit={onSubmitMock} />
    );

    expect(onSubmitMock).not.toHaveBeenCalled();
    await user.type(getByRole('textbox'), '{enter}');
    expect(onSubmitMock).toHaveBeenCalled();
  });

  it('should not call onSubmit when pressing the enter key with less then 4 non digit input', async () => {
    const user = userEvent.setup();
    const onSubmitMock = jest.fn();
    const { getByRole } = render(
      <AiAssistToolbarInput {...testProps} value="2abc213" onSubmit={onSubmitMock} />
    );

    await user.type(getByRole('textbox'), '{enter}');
    expect(onSubmitMock).not.toHaveBeenCalled();
  });

  it('should show an info msg when pressing the enter key with less then 4 non digit input', async () => {
    const user = userEvent.setup();
    const onSubmitMock = jest.fn();
    const { getByRole } = render(
      <AiAssistToolbarInput {...testProps} value="2abc213" onSubmit={onSubmitMock} />
    );

    await user.type(getByRole('textbox'), '{enter}');
    expect(huePubSub.publish).toHaveBeenCalledWith('hue.global.info', {
      message: 'Please use at least 4 letters in your prompt'
    });
  });

  it('should call onChange callback when input value changes', async () => {
    const user = userEvent.setup();
    const onChangeMock = jest.fn();
    const { getByRole } = render(
      <AiAssistToolbarInput {...testProps} onInputChanged={onChangeMock} />
    );

    const inputElement = getByRole('textbox', {
      name: 'Press down arrow to select from history'
    });
    await user.type(inputElement, 'abcd');
    expect(onChangeMock).toHaveBeenCalledWith('a');
    expect(onChangeMock).toHaveBeenCalledWith('b');
    expect(onChangeMock).toHaveBeenCalledWith('c');
    expect(onChangeMock).toHaveBeenCalledWith('d');
  });
});
