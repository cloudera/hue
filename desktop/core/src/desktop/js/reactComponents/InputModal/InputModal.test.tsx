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
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import InputModal from './InputModal';

describe('InputModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSubmit = jest.fn();

  it('should render custom modal title', () => {
    const inputModal = render(
      <InputModal
        title="Custom title"
        inputLabel="Enter File name here"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue=""
        inputType="text"
      />
    );
    expect(inputModal.getByText('Custom title')).toBeVisible();
  });

  it('should render custom input label', () => {
    const inputModal = render(
      <InputModal
        title="Create File"
        inputLabel="Custom input label"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue=""
        inputType="text"
      />
    );
    expect(inputModal.getByText('Custom input label')).toBeVisible();
  });

  it('should call onSubmit when create button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <InputModal
        title="Create File"
        inputLabel="Enter File name here"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue=""
        inputType="text"
      />
    );
    const submitButton = screen.getByRole('button', { name: 'Create' });

    expect(mockOnSubmit).not.toHaveBeenCalled();

    const inputField = screen.getByRole('textbox');
    await user.type(inputField, 'test-file.txt');

    await user.click(submitButton);
    waitFor(() => expect(mockOnSubmit).toHaveBeenCalled());
  });

  it('should call onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <InputModal
        title="Create File"
        inputLabel="Enter File name here"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue=""
        inputType="text"
      />
    );
    const closeButton = screen.getByRole('button', { name: 'Cancel' });

    expect(mockOnClose).not.toHaveBeenCalled();
    await user.click(closeButton);
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should render modal with input visible', () => {
    render(
      <InputModal
        title="Create File"
        inputLabel="Custom input label"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue=""
        inputType="text"
      />
    );
    const input = screen.getByRole('textbox');
    expect(input).toBeVisible();
  });

  it('should render modal with number input when input type is number', () => {
    render(
      <InputModal
        title="Set replication"
        inputLabel="Custom input label"
        submitText="Submit"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue={2}
        inputType="number"
      />
    );
    const input = screen.getByRole('spinbutton');
    expect(input).toBeVisible();
  });

  it('should render modal with empty input value when intial value is empty', () => {
    render(
      <InputModal
        title="Create File"
        inputLabel="Custom input label"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue=""
        inputType="text"
      />
    );
    expect(screen.getByRole('textbox')).toHaveValue('');
  });

  it('should render modal with intial value in input while input type is text', () => {
    render(
      <InputModal
        title="Create File"
        inputLabel="Custom input label"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue="hello"
        inputType="text"
      />
    );
    expect(screen.getByRole('textbox')).toHaveValue('hello');
  });

  it('should render modal with intial value in input while input type is number', () => {
    render(
      <InputModal
        title="Create File"
        inputLabel="Custom input label"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue={2}
        inputType="number"
      />
    );
    expect(screen.getByRole('spinbutton')).toHaveValue(2);
  });

  it('should accept tab focus on input elements placed in the drawer', async () => {
    const user = userEvent.setup();
    render(
      <InputModal
        title="Create File"
        inputLabel="Custom input label"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue=""
        inputType="text"
      />
    );
    const inputModal = screen.getByRole('dialog', { name: 'Create File' });
    const inputTextBox = within(inputModal).getByRole('textbox');
    const submitButton = within(inputModal).getByRole('button', { name: 'Create' });
    const cancelButton = within(inputModal).getByRole('button', { name: 'Cancel' });

    const inputField = screen.getByRole('textbox');
    await user.type(inputField, 'test-file.txt');

    expect(inputTextBox).toHaveFocus();
    await user.tab();
    waitFor(() => expect(submitButton).toHaveFocus());
    await user.tab();
    expect(cancelButton).toHaveFocus();
  });

  it('should disable the submit button when isLoading is true', () => {
    render(
      <InputModal
        title="Create File"
        inputLabel="Custom input label"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue=""
        inputType="text"
        loading={true}
      />
    );
    const submitButton = screen.getByRole('button', { name: 'loading Create' });
    expect(submitButton).toBeInTheDocument();
  });

  it('should disable the submit button when input value is same as initial value', async () => {
    const user = userEvent.setup();
    render(
      <InputModal
        title="Create File"
        inputLabel="Custom input label"
        submitText="Create"
        showModal={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
        initialValue="sample_file.txt"
        inputType="text"
      />
    );

    const submitButton = screen.getByRole('button', { name: 'Create' });
    expect(submitButton).toBeDisabled();

    const inputField = screen.getByRole('textbox');
    await user.type(inputField, 'test-file.txt');
    waitFor(() => expect(submitButton).not.toBeDisabled());
  });
});
