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
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import FormInput, { FieldType, BaseFieldConfig } from './FormInput';

describe('FormInput Component', () => {
  const mockOnChange = jest.fn();
  const defaultProps = {
    loading: false,
    onChange: mockOnChange
  };

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  describe('INPUT field type', () => {
    const inputField: BaseFieldConfig = {
      name: 'testInput',
      type: FieldType.INPUT,
      label: 'Test Input',
      placeholder: 'Enter text',
      className: 'test-class'
    };

    it('should render input field with correct props', () => {
      render(<FormInput field={inputField} value="test value" {...defaultProps} />);

      const input = screen.getByDisplayValue('test value');
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('placeholder', 'Enter text');
      expect(input).toHaveClass('test-class');
    });

    it('should call onChange when input value changes', () => {
      render(<FormInput field={inputField} value="" {...defaultProps} />);

      const input = screen.getByPlaceholderText('Enter text');
      fireEvent.change(input, { target: { value: 'new value' } });

      expect(mockOnChange).toHaveBeenCalledWith('testInput', 'new value');
    });

    it('should render label for input field', () => {
      render(<FormInput field={inputField} value="" {...defaultProps} />);

      expect(screen.getByText('Test Input')).toBeInTheDocument();
    });

    it('should render tooltip icon when tooltip is provided', () => {
      const inputWithTooltip: BaseFieldConfig = {
        name: 'testInputTooltip',
        type: FieldType.INPUT,
        label: 'Input with Tooltip',
        tooltip: 'This is an input tooltip'
      };

      render(<FormInput field={inputWithTooltip} value="" {...defaultProps} />);

      expect(screen.getByRole('img', { name: /info-circle/i })).toBeInTheDocument();
    });

    it('should handle visibility conditions - render when not hidden', () => {
      const visibilityField: BaseFieldConfig = {
        name: 'conditionalField',
        type: FieldType.INPUT,
        label: 'Conditional Field',
        hidden: false
      };

      render(<FormInput field={visibilityField} value="" {...defaultProps} />);

      expect(screen.queryByDisplayValue('')).toBeInTheDocument();
      expect(screen.queryByRole('textbox', { name: /conditional field/i })).toBeInTheDocument();
    });

    it('should handle visibility conditions - not render when hidden', () => {
      const visibilityField: BaseFieldConfig = {
        name: 'conditionalField',
        type: FieldType.INPUT,
        label: 'Conditional Field',
        hidden: true
      };

      render(<FormInput field={visibilityField} value="" {...defaultProps} />);

      expect(screen.queryByRole('textbox', { name: /conditional field/i })).not.toBeInTheDocument();
    });
  });

  describe('SELECT field type', () => {
    const selectField: BaseFieldConfig = {
      name: 'testSelect',
      type: FieldType.SELECT,
      label: 'Test Select',
      placeholder: 'Choose option',
      options: [
        { value: 'option1', label: 'Option 1' },
        { value: 'option2', label: 'Option 2' }
      ]
    };

    it('should render select field with options', () => {
      render(<FormInput field={selectField} value="option1" {...defaultProps} />);

      const select = screen.getByRole('combobox');
      expect(select).toBeInTheDocument();
      expect(screen.getByText('Option 1')).toBeInTheDocument();
    });

    it('should call onChange when select value changes', async () => {
      const user = userEvent.setup();
      const onChangeSpy = jest.fn();
      render(
        <FormInput field={selectField} value="option1" onChange={onChangeSpy} loading={false} />
      );

      const select = screen.getByRole('combobox');
      expect(select).toBeInTheDocument();

      expect(screen.getByText('Option 1')).toBeInTheDocument();
      await user.click(select);

      const option2 = screen.getByText('Option 2');
      await user.click(option2);

      expect(onChangeSpy).toHaveBeenCalledWith('testSelect', 'option2');
    });

    it('should render tooltip icon when tooltip is provided', () => {
      const selectWithTooltip: BaseFieldConfig = {
        name: 'testSelectTooltip',
        type: FieldType.SELECT,
        label: 'Select with Tooltip',
        tooltip: 'This is a select tooltip',
        options: [{ value: 'option1', label: 'Option 1' }]
      };

      render(<FormInput field={selectWithTooltip} value="" {...defaultProps} />);

      expect(screen.getByRole('img', { name: /info-circle/i })).toBeInTheDocument();
    });
  });

  describe('CHECKBOX field type', () => {
    const checkboxField: BaseFieldConfig = {
      name: 'testCheckbox',
      type: FieldType.CHECKBOX,
      label: 'Test Checkbox',
      tooltip: 'This is a tooltip'
    };

    it('should render checkbox field', () => {
      render(<FormInput field={checkboxField} value={true} {...defaultProps} />);

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).toBeChecked();
      expect(screen.getByText('Test Checkbox')).toBeInTheDocument();
    });

    it('should call onChange when checkbox is toggled', () => {
      render(<FormInput field={checkboxField} value={false} {...defaultProps} />);

      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);

      expect(mockOnChange).toHaveBeenCalledWith('testCheckbox', true);
    });

    it('should render when default value is true', () => {
      render(<FormInput field={checkboxField} defaultValue={true} {...defaultProps} />);

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).toBeChecked();
    });

    it('should render when default value is false', () => {
      render(<FormInput field={checkboxField} defaultValue={false} {...defaultProps} />);

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).not.toBeChecked();
    });

    it('should render tooltip icon when tooltip is provided', () => {
      render(<FormInput field={checkboxField} value={false} {...defaultProps} />);

      expect(screen.getByRole('img', { name: /info-circle/i })).toBeInTheDocument();
    });
  });

  describe('RADIO field type', () => {
    const radioField: BaseFieldConfig = {
      name: 'testRadio',
      type: FieldType.RADIO,
      label: 'Test Radio',
      options: [
        { value: 'radio1', label: 'Radio 1' },
        { value: 'radio2', label: 'Radio 2' }
      ]
    };

    it('should render radio group with options', () => {
      render(<FormInput field={radioField} value="radio1" {...defaultProps} />);

      expect(screen.getByText('Radio 1')).toBeInTheDocument();
      expect(screen.getByText('Radio 2')).toBeInTheDocument();

      const radio1 = screen.getByDisplayValue('radio1');
      const radio2 = screen.getByDisplayValue('radio2');

      expect(radio1).toBeChecked();
      expect(radio2).not.toBeChecked();
    });

    it('should call onChange when radio option changes', () => {
      render(<FormInput field={radioField} value="radio1" {...defaultProps} />);

      const radio2 = screen.getByDisplayValue('radio2');
      fireEvent.click(radio2);

      expect(mockOnChange).toHaveBeenCalledWith('testRadio', 'radio2');
    });

    it('should render with default value', () => {
      render(
        <FormInput field={radioField} defaultValue="radio2" value={undefined} {...defaultProps} />
      );

      const radio2 = screen.getByDisplayValue('radio2');
      expect(radio2).toBeChecked();
    });

    it('should render tooltip icon when tooltip is provided', () => {
      const radioWithTooltip: BaseFieldConfig = {
        name: 'testRadioTooltip',
        type: FieldType.RADIO,
        label: 'Radio with Tooltip',
        tooltip: 'This is a radio tooltip',
        options: [{ value: 'radio1', label: 'Radio 1' }]
      };

      render(<FormInput field={radioWithTooltip} value="" {...defaultProps} />);

      expect(screen.getByRole('img', { name: /info-circle/i })).toBeInTheDocument();
    });
  });
});
