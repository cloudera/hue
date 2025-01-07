import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoadingErrorWrapper from './LoadingErrorWrapper';

describe('LoadingErrorWrapper', () => {
  const defaultProps = {
    loading: false,
    errors: [],
    children: <div>Children Content</div>
  };

  it('should render loading spinner when loading is true', () => {
    const { getAllByTestId, queryByText } = render(
      <LoadingErrorWrapper {...defaultProps} loading={true} />
    );

    expect(getAllByTestId('loading-error-wrapper__sppiner')).toHaveLength(2);
    expect(queryByText('Children Content')).toBeInTheDocument();
  });

  it('should render children when loading is false and no errors', () => {
    const { getByText } = render(<LoadingErrorWrapper {...defaultProps} loading={false} />);

    expect(getByText('Children Content')).toBeInTheDocument();
  });

  it('should render error messages when there are enabled errors', () => {
    const errors = [
      { enabled: true, message: 'Error 1' },
      { enabled: false, message: 'Error 2' }
    ];

    const { getByText, queryByText } = render(
      <LoadingErrorWrapper {...defaultProps} errors={errors} loading={false} />
    );

    expect(getByText('Error 1')).toBeInTheDocument();
    expect(queryByText('Error 2')).not.toBeInTheDocument();
  });

  it('should render action button for errors with onClick', () => {
    const mockOnClick = jest.fn();
    const errors = [
      { enabled: true, message: 'Error with action', action: 'Retry', onClick: mockOnClick }
    ];

    const { getByText } = render(
      <LoadingErrorWrapper {...defaultProps} errors={errors} loading={false} />
    );

    const button = getByText('Retry');
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(mockOnClick).toHaveBeenCalled();
  });

  it('should render multiple errors if there are multiple enabled errors', () => {
    const errors = [
      { enabled: true, message: 'Error 1' },
      { enabled: true, message: 'Error 2' }
    ];

    const { getByText } = render(
      <LoadingErrorWrapper {...defaultProps} errors={errors} loading={false} />
    );

    expect(getByText('Error 1')).toBeInTheDocument();
    expect(getByText('Error 2')).toBeInTheDocument();
  });
});
