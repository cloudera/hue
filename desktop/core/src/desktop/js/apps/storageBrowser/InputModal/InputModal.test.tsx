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

import InputModal from './InputModal';

describe('InputModal', () => {
  test('renders custom modal title', () => {
    const inputModal = render(
      <InputModal
        title={'Custom title'}
        inputLabel={'Enter File name here'}
        submitText={'Create'}
        showModal={true}
        onSubmit={jest.fn()}
        onClose={jest.fn()}
        initialValue={''}
        inputType={'text'}
      />
    );
    expect(inputModal.getByText('Custom title')).toBeVisible();
  });

  test('renders custom input label', () => {
    const inputModal = render(
      <InputModal
        title={'Create New File'}
        inputLabel={'Custom input label'}
        submitText={'Create'}
        showModal={true}
        onSubmit={jest.fn()}
        onClose={jest.fn()}
        initialValue={''}
        inputType={'text'}
      />
    );
    expect(inputModal.getByText('Custom input label')).toBeVisible();
  });

  test('calls onSubmit when create button is clicked', async () => {
    const onCloseMock = jest.fn();
    const onSubmitMock = jest.fn();
    const user = userEvent.setup();
    render(
      <InputModal
        title={'Create New File'}
        inputLabel={'Enter File name here'}
        submitText={'Create'}
        showModal={true}
        onSubmit={onSubmitMock}
        onClose={onCloseMock}
        initialValue={''}
        inputType={'text'}
      />
    );
    const submitButton = screen.getByRole('button', { name: 'Create' });

    expect(onSubmitMock).not.toHaveBeenCalled();
    await user.click(submitButton);
    expect(onSubmitMock).toHaveBeenCalled();
  });

  test('calls onClose after submission when submit button is clicked', async () => {
    const onCloseMock = jest.fn();
    const onSubmitMock = jest.fn();
    const user = userEvent.setup();
    render(
      <InputModal
        title={'Create New File'}
        inputLabel={'Enter File name here'}
        submitText={'Create'}
        showModal={true}
        onSubmit={onSubmitMock}
        onClose={onCloseMock}
        initialValue={''}
        inputType={'text'}
      />
    );
    const submitButton = screen.getByRole('button', { name: 'Create' });

    await user.click(submitButton);
    expect(onSubmitMock).toHaveBeenCalled();
    expect(onCloseMock).toHaveBeenCalled();
  });

  test('calls onClose when close button is clicked', async () => {
    const onCloseMock = jest.fn();
    const onSubmitMock = jest.fn();
    const user = userEvent.setup();
    render(
      <InputModal
        title={'Create New File'}
        inputLabel={'Enter File name here'}
        submitText={'Create'}
        showModal={true}
        onSubmit={onSubmitMock}
        onClose={onCloseMock}
        initialValue={''}
        inputType={'text'}
      />
    );
    const closeButton = screen.getByRole('button', { name: 'Cancel' });

    expect(onCloseMock).not.toHaveBeenCalled();
    await user.click(closeButton);
    expect(onCloseMock).toHaveBeenCalled();
  });

  test('renders modal with input visible', () => {
    render(
      <InputModal
        title={'Create New File'}
        inputLabel={'Custom input label'}
        submitText={'Create'}
        showModal={true}
        onSubmit={jest.fn()}
        onClose={jest.fn()}
        initialValue={''}
        inputType={'text'}
      />
    );
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('hue-input-modal__input');
    expect(input).toBeVisible();
  });

  test('renders modal with number input when input type is number', () => {
    render(
      <InputModal
        title={'Set replication'}
        inputLabel={'Custom input label'}
        submitText={'Submit'}
        showModal={true}
        onSubmit={jest.fn()}
        onClose={jest.fn()}
        initialValue={2}
        inputType={'number'}
      />
    );
    const input = screen.getByRole('spinbutton');
    expect(input).toHaveClass('hue-input-modal__input');
    expect(input).toBeVisible();
  });

  test('renders modal with empty input value when intial value is empty', () => {
    render(
      <InputModal
        title={'Create New File'}
        inputLabel={'Custom input label'}
        submitText={'Create'}
        showModal={true}
        onSubmit={jest.fn()}
        onClose={jest.fn()}
        initialValue={''}
        inputType={'text'}
      />
    );
    expect(screen.getByRole('textbox')).toHaveValue('');
  });

  test('renders modal with intial value in input while input type is text', () => {
    render(
      <InputModal
        title={'Create New File'}
        inputLabel={'Custom input label'}
        submitText={'Create'}
        showModal={true}
        onSubmit={jest.fn()}
        onClose={jest.fn()}
        initialValue={'hello'}
        inputType={'text'}
      />
    );
    expect(screen.getByRole('textbox')).toHaveValue('hello');
  });

  test('renders modal with intial value in input while input type is number', () => {
    render(
      <InputModal
        title={'Create New File'}
        inputLabel={'Custom input label'}
        submitText={'Create'}
        showModal={true}
        onSubmit={jest.fn()}
        onClose={jest.fn()}
        initialValue={2}
        inputType={'number'}
      />
    );
    expect(screen.getByRole('spinbutton')).toHaveValue(2);
  });

  test('accepts tab focus on input elements placed in the drawer', async () => {
    const user = userEvent.setup();
    render(
      <InputModal
        title={'Create New File'}
        inputLabel={'Custom input label'}
        submitText={'Create'}
        showModal={true}
        onSubmit={jest.fn()}
        onClose={jest.fn()}
        initialValue={''}
        inputType={'text'}
      />
    );
    const inputModal = screen.getByRole('dialog', { name: 'Create New File' });
    const closeIconButton = within(inputModal).getByRole('button', { name: 'Close' });
    const inputTextBox = within(inputModal).getByRole('textbox');
    const submitButton = within(inputModal).getByRole('button', { name: 'Create' });
    const cancelButton = within(inputModal).getByRole('button', { name: 'Cancel' });

    await user.tab();
    if (!closeIconButton.matches(':focus')) {
      await user.tab(); // Tab again if the focus is on the sentinel
    }
    expect(closeIconButton).toHaveFocus();
    await user.tab();
    expect(inputTextBox).toHaveFocus();
    await user.tab();
    expect(submitButton).toHaveFocus();
    await user.tab();
    expect(cancelButton).toHaveFocus();
  });
});
