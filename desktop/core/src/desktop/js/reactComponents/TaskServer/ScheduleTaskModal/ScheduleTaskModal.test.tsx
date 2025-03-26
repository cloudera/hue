import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScheduleTaskModal from './ScheduleTaskModal';
import { scheduleTasksCategory } from '../constants';

const mockHandleSubmit = jest.fn();
jest.mock('../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockHandleSubmit,
    loading: false,
    error: null
  }))
}));

describe('ScheduleTaskModal', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the radio group', () => {
    render(<ScheduleTaskModal onClose={mockOnClose} />);
    const radioGroup = screen.getAllByRole('radio');
    expect(radioGroup).toHaveLength(2);
    expect(radioGroup[0]).toBeInTheDocument();
    expect(radioGroup[0]).toHaveAttribute('value', scheduleTasksCategory[0].value);
    expect(radioGroup[1]).toBeInTheDocument();
    expect(radioGroup[1]).toHaveAttribute('value', scheduleTasksCategory[1].value);
  });

  it('should render one input when document_cleanup is selected', () => {
    render(<ScheduleTaskModal onClose={mockOnClose} />);
    const radioGroup = screen.getAllByRole('radio');

    fireEvent.click(radioGroup[0]);

    const inputs = screen.getAllByRole('spinbutton');
    expect(inputs).toHaveLength(1);
    expect(inputs[0]).toBeInTheDocument();
    expect(inputs[0]).toHaveAttribute('name', scheduleTasksCategory[0].children[0].value);
  });

  it('should render one input when temp_cleanup is selected', () => {
    render(<ScheduleTaskModal onClose={mockOnClose} />);
    const radioGroup = screen.getAllByRole('radio');

    fireEvent.click(radioGroup[1]);

    const inputs = screen.getAllByRole('spinbutton');
    expect(inputs).toHaveLength(2);
    expect(inputs[0]).toBeInTheDocument();
    expect(inputs[0]).toHaveAttribute('name', scheduleTasksCategory[1].children[0].value);
    expect(inputs[1]).toBeInTheDocument();
    expect(inputs[1]).toHaveAttribute('name', scheduleTasksCategory[1].children[1].value);
  });

  it('should call onClose when the close button is clicked', () => {
    render(<ScheduleTaskModal onClose={mockOnClose} />);
    const closeButton = screen.getByRole('button', { name: 'Close' });

    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should trigger handleSubmit when the submit button is clicked', () => {
    const mockHandleSubmit = jest.fn();
    render(<ScheduleTaskModal onClose={mockOnClose} />);
    const submitButton = screen.getByRole('button', { name: /submit/i });

    fireEvent.click(submitButton);

    waitFor(() => expect(mockHandleSubmit).toHaveBeenCalledTimes(1));
  });
});
