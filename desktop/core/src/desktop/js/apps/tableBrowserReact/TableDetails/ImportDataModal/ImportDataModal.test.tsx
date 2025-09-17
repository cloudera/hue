// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ImportDataModal from './ImportDataModal';
import { post } from '../../../../api/utils';
import huePubSub from '../../../../utils/huePubSub';
import { notifyError } from '../../utils/notifier';
import type { Connector, Namespace, Compute } from '../../../../config/types';

// Mock dependencies
jest.mock('../../../../utils/i18nReact', () => ({
  i18nReact: {
    useTranslation: () => ({
      t: (key: string, options?: Record<string, unknown>) => {
        if (options) {
          return key.replace(/\{\{(\w+)\}\}/g, (match, prop) => String(options[prop] || match));
        }
        return key;
      }
    })
  }
}));

jest.mock('../../../../api/utils', () => ({
  post: jest.fn()
}));

jest.mock('../../../../utils/huePubSub', () => ({
  __esModule: true,
  default: {
    publish: jest.fn()
  }
}));

jest.mock('../../utils/notifier', () => ({
  notifyError: jest.fn()
}));

jest.mock('../../utils/connector', () => ({
  getConnectorIdOrType: jest.fn(() => 'hive')
}));

// Mock PathBrowser component
jest.mock('../../../../reactComponents/PathBrowser/PathBrowser', () => {
  return function MockPathBrowser({
    filePath,
    onFilepathChange
  }: {
    filePath: string;
    onFilepathChange: (path: string) => void;
  }) {
    return (
      <input
        data-testid="path-browser"
        value={filePath}
        onChange={e => onFilepathChange(e.target.value)}
        placeholder="Enter file path"
      />
    );
  };
});

// Mock CUIX Modal
jest.mock('cuix/dist/components/Modal', () => {
  return function MockModal({
    open,
    title,
    onCancel,
    onOk,
    okButtonProps,
    children
  }: {
    open: boolean;
    title: string;
    onCancel: () => void;
    onOk: () => void;
    okButtonProps?: { disabled?: boolean; loading?: boolean };
    children: React.ReactNode;
  }) {
    return open ? (
      <div data-testid="modal" role="dialog">
        <div data-testid="modal-title">{title}</div>
        <div data-testid="modal-content">{children}</div>
        <button data-testid="modal-cancel" onClick={onCancel}>
          Cancel
        </button>
        <button data-testid="modal-ok" onClick={onOk} disabled={okButtonProps?.disabled}>
          Submit
        </button>
      </div>
    ) : null;
  };
});

describe('ImportDataModal', () => {
  const mockConnector: Connector = {
    id: 'hive',
    dialect: 'hive',
    displayName: 'Hive',
    buttonName: 'Hive',
    tooltip: 'Hive',
    page: '/hive',
    type: 'hive'
  };

  const mockNamespace: Namespace = {
    id: 'default-namespace',
    name: 'default',
    status: 'CREATED',
    computes: []
  };

  const mockCompute: Compute = {
    id: 'default-compute',
    name: 'default',
    type: 'direct'
  };

  const defaultProps = {
    open: true,
    onCancel: jest.fn(),
    database: 'test_db',
    table: 'test_table',
    connector: mockConnector,
    namespace: mockNamespace,
    compute: mockCompute,
    sourceType: 'hive',
    partitionColumns: []
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (post as jest.Mock).mockResolvedValue({ status: 0, history_uuid: 'test-uuid' });
  });

  describe('Modal Rendering', () => {
    it('should render modal when open is true', () => {
      render(<ImportDataModal {...defaultProps} />);

      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByTestId('modal-title')).toHaveTextContent('Import Data');
    });

    it('should not render modal when open is false', () => {
      render(<ImportDataModal {...defaultProps} open={false} />);

      expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
    });

    it('should render file path input', () => {
      render(<ImportDataModal {...defaultProps} />);

      expect(screen.getByTestId('path-browser')).toBeInTheDocument();
      // Check for the Path label - use a function matcher to handle the asterisk
      expect(
        screen.getByText((content, element) => {
          return element?.textContent === 'Path *';
        })
      ).toBeInTheDocument();
    });

    it('should render overwrite checkbox', () => {
      render(<ImportDataModal {...defaultProps} />);

      expect(screen.getByRole('checkbox')).toBeInTheDocument();
      expect(screen.getByText('Overwrite existing data')).toBeInTheDocument();
    });

    it('should render warning message', () => {
      render(<ImportDataModal {...defaultProps} />);

      expect(screen.getByText(/Note that loading data will move data/)).toBeInTheDocument();
    });
  });

  describe('Partition Columns', () => {
    it('should render partition column inputs when partitionColumns are provided', () => {
      const partitionColumns = [
        { name: 'year', value: '' },
        { name: 'month', value: '' }
      ];

      render(<ImportDataModal {...defaultProps} partitionColumns={partitionColumns} />);

      expect(screen.getByText('Partition Values')).toBeInTheDocument();
      expect(screen.getByText('year')).toBeInTheDocument();
      expect(screen.getByText('month')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter value for year')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter value for month')).toBeInTheDocument();
    });

    it('should not render partition section when no partition columns', () => {
      render(<ImportDataModal {...defaultProps} partitionColumns={[]} />);

      expect(screen.queryByText('Partition Values')).not.toBeInTheDocument();
    });

    it('should initialize partition values from props', () => {
      const partitionColumns = [
        { name: 'year', value: '2023' },
        { name: 'month', value: '12' }
      ];

      render(<ImportDataModal {...defaultProps} partitionColumns={partitionColumns} />);

      const yearInput = screen.getByPlaceholderText('Enter value for year') as HTMLInputElement;
      const monthInput = screen.getByPlaceholderText('Enter value for month') as HTMLInputElement;

      expect(yearInput.value).toBe('2023');
      expect(monthInput.value).toBe('12');
    });
  });

  describe('Form Validation', () => {
    it('should disable submit button when file path is empty', () => {
      render(<ImportDataModal {...defaultProps} />);

      const submitButton = screen.getByTestId('modal-ok');
      expect(submitButton).toBeDisabled();
    });

    it('should enable submit button when file path is provided', async () => {
      const user = userEvent.setup();
      render(<ImportDataModal {...defaultProps} />);

      const pathInput = screen.getByTestId('path-browser');
      await user.type(pathInput, '/path/to/data.csv');

      const submitButton = screen.getByTestId('modal-ok');
      expect(submitButton).not.toBeDisabled();
    });

    it('should prevent form submission when file path is empty', () => {
      render(<ImportDataModal {...defaultProps} />);

      // Submit button should be disabled when file path is empty
      const submitButton = screen.getByTestId('modal-ok');
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Form Submission', () => {
    it('should submit form with correct data', async () => {
      const user = userEvent.setup();
      render(<ImportDataModal {...defaultProps} />);

      // Fill in file path
      const pathInput = screen.getByTestId('path-browser');
      await user.type(pathInput, '/path/to/data.csv');

      // Check overwrite
      const overwriteCheckbox = screen.getByRole('checkbox');
      await user.click(overwriteCheckbox);

      // Submit form
      const submitButton = screen.getByTestId('modal-ok');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(post).toHaveBeenCalledWith(
          '/metastore/table/test_db/test_table/load',
          expect.any(URLSearchParams),
          {
            silenceErrors: false,
            qsEncodeData: false
          }
        );
      });

      // Verify form data
      const formData = (post as jest.Mock).mock.calls[0][1] as URLSearchParams;
      expect(formData.get('path')).toBe('/path/to/data.csv');
      expect(formData.get('overwrite')).toBe('on');
      expect(formData.get('is_embeddable')).toBe('true');
      expect(formData.get('source_type')).toBe('hive');
    });

    it('should submit partition values when provided', async () => {
      const user = userEvent.setup();
      const partitionColumns = [
        { name: 'year', value: '' },
        { name: 'month', value: '' }
      ];

      render(<ImportDataModal {...defaultProps} partitionColumns={partitionColumns} />);

      // Fill in file path
      const pathInput = screen.getByTestId('path-browser');
      await user.type(pathInput, '/path/to/data.csv');

      // Fill in partition values
      const yearInput = screen.getByPlaceholderText('Enter value for year');
      const monthInput = screen.getByPlaceholderText('Enter value for month');
      await user.type(yearInput, '2023');
      await user.type(monthInput, '12');

      // Submit form
      const submitButton = screen.getByTestId('modal-ok');
      fireEvent.click(submitButton);

      await waitFor(() => {
        const formData = (post as jest.Mock).mock.calls[0][1] as URLSearchParams;
        expect(formData.get('year')).toBe('2023');
        expect(formData.get('month')).toBe('12');
      });
    });

    it('should include namespace and compute in form data', async () => {
      const user = userEvent.setup();
      render(<ImportDataModal {...defaultProps} />);

      const pathInput = screen.getByTestId('path-browser');
      await user.type(pathInput, '/path/to/data.csv');

      const submitButton = screen.getByTestId('modal-ok');
      fireEvent.click(submitButton);

      await waitFor(() => {
        const formData = (post as jest.Mock).mock.calls[0][1] as URLSearchParams;
        expect(formData.get('namespace')).toBe(JSON.stringify(mockNamespace));
        expect(formData.get('cluster')).toBe(JSON.stringify(mockCompute));
      });
    });
  });

  describe('Response Handling', () => {
    it('should close modal and publish event on successful submission', async () => {
      const user = userEvent.setup();
      const onCancel = jest.fn();

      render(<ImportDataModal {...defaultProps} onCancel={onCancel} />);

      const pathInput = screen.getByTestId('path-browser');
      await user.type(pathInput, '/path/to/data.csv');

      const submitButton = screen.getByTestId('modal-ok');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(huePubSub.publish).toHaveBeenCalledWith('notebook.task.submitted', {
          status: 0,
          history_uuid: 'test-uuid'
        });
        expect(onCancel).toHaveBeenCalled();
      });
    });

    it('should show error message on validation failure', async () => {
      const user = userEvent.setup();
      (post as jest.Mock).mockResolvedValue({
        status: 1,
        data: 'Invalid file path'
      });

      render(<ImportDataModal {...defaultProps} />);

      const pathInput = screen.getByTestId('path-browser');
      await user.type(pathInput, '/invalid/path');

      const submitButton = screen.getByTestId('modal-ok');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Invalid file path')).toBeInTheDocument();
      });
    });

    it('should call notifyError on request failure', async () => {
      const user = userEvent.setup();
      (post as jest.Mock).mockRejectedValue(new Error('Network error'));

      render(<ImportDataModal {...defaultProps} />);

      const pathInput = screen.getByTestId('path-browser');
      await user.type(pathInput, '/path/to/data.csv');

      const submitButton = screen.getByTestId('modal-ok');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(notifyError).toHaveBeenCalledWith('Failed to import data');
      });
    });
  });

  describe('Form Reset', () => {
    it('should reset form when modal is closed and reopened', async () => {
      const user = userEvent.setup();
      const { rerender } = render(<ImportDataModal {...defaultProps} />);

      // Fill in data
      const pathInput = screen.getByTestId('path-browser');
      await user.type(pathInput, '/path/to/data.csv');

      const overwriteCheckbox = screen.getByRole('checkbox');
      await user.click(overwriteCheckbox);

      // Close modal
      rerender(<ImportDataModal {...defaultProps} open={false} />);

      // Reopen modal
      rerender(<ImportDataModal {...defaultProps} open={true} />);

      // Form should be reset
      const newPathInput = screen.getByTestId('path-browser') as HTMLInputElement;
      const newOverwriteCheckbox = screen.getByRole('checkbox') as HTMLInputElement;

      expect(newPathInput.value).toBe('');
      expect(newOverwriteCheckbox.checked).toBe(false);
    });

    it('should reset partition values when modal is reopened', async () => {
      const user = userEvent.setup();
      const partitionColumns = [{ name: 'year', value: '' }];
      const { rerender } = render(
        <ImportDataModal {...defaultProps} partitionColumns={partitionColumns} />
      );

      // Fill in partition value
      const yearInput = screen.getByPlaceholderText('Enter value for year');
      await user.type(yearInput, '2023');

      // Close and reopen modal
      rerender(
        <ImportDataModal {...defaultProps} partitionColumns={partitionColumns} open={false} />
      );
      rerender(
        <ImportDataModal {...defaultProps} partitionColumns={partitionColumns} open={true} />
      );

      // Partition value should be reset
      const newYearInput = screen.getByPlaceholderText('Enter value for year') as HTMLInputElement;
      expect(newYearInput.value).toBe('');
    });
  });

  describe('Loading States', () => {
    it('should show loading state during submission', async () => {
      const user = userEvent.setup();
      let resolvePost: (value: unknown) => void;
      const postPromise = new Promise(resolve => {
        resolvePost = resolve;
      });
      (post as jest.Mock).mockReturnValue(postPromise);

      render(<ImportDataModal {...defaultProps} />);

      const pathInput = screen.getByTestId('path-browser');
      await user.type(pathInput, '/path/to/data.csv');

      const submitButton = screen.getByTestId('modal-ok');
      fireEvent.click(submitButton);

      // Should be disabled during loading
      expect(submitButton).toBeDisabled();

      // Resolve the promise
      resolvePost!({ status: 0, history_uuid: 'test-uuid' });

      await waitFor(() => {
        expect(submitButton).not.toBeDisabled();
      });
    });
  });
});
