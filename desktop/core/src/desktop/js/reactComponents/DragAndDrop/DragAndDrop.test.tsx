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
import { render, fireEvent, waitFor, act, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import DragAndDrop from './DragAndDrop';

const createMockFile = (name = 'test.txt', content = 'file content', type = 'text/plain') => {
  const file = new File([content], name, { type });
  Object.defineProperty(file, 'size', { value: content.length });
  return file;
};

const createDragEvent = (files: File[]) => ({
  dataTransfer: {
    files,
    items: files.map(file => ({
      kind: 'file',
      type: file.type,
      getAsFile: () => file
    })),
    types: ['Files']
  }
});

describe('DragAndDrop', () => {
  const mockOnDrop = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the default message when no children provided', () => {
    render(<DragAndDrop onDrop={mockOnDrop} />);

    expect(screen.getByText('Select file')).toBeInTheDocument();
    expect(screen.getByText('Browse files or drag and drop files')).toBeInTheDocument();
  });

  it('should render children when provided and not dragging', () => {
    render(
      <DragAndDrop onDrop={mockOnDrop}>
        <div>Custom Child Element</div>
      </DragAndDrop>
    );

    expect(screen.getByText('Custom Child Element')).toBeInTheDocument();
    expect(screen.queryByText('Browse files or drag and drop files')).not.toBeInTheDocument();
  });

  it('should handle single file selection', async () => {
    const user = userEvent.setup();
    render(<DragAndDrop onDrop={mockOnDrop} />);

    const fileInput = screen.getByTestId('drag-drop__input');
    const file = createMockFile();

    await user.upload(fileInput, file);

    // react-dropzone calls onDrop with (acceptedFiles, fileRejections, event)
    expect(mockOnDrop).toHaveBeenCalledWith(expect.arrayContaining([file]), [], expect.any(Object));
  });

  it('should handle multiple file selection', async () => {
    const user = userEvent.setup();
    render(<DragAndDrop onDrop={mockOnDrop} />);

    const fileInput = screen.getByTestId('drag-drop__input');
    const files = [
      createMockFile('file1.txt'),
      createMockFile('file2.txt'),
      createMockFile('file3.jpg', 'image content', 'image/jpeg')
    ];

    await user.upload(fileInput, files);

    // react-dropzone calls onDrop with (acceptedFiles, fileRejections, event)
    expect(mockOnDrop).toHaveBeenCalledWith(files, [], expect.any(Object));
  });

  it('should display drop message when dragging files over the component', async () => {
    render(<DragAndDrop onDrop={mockOnDrop} />);

    const dropzone = screen.getByTestId('drag-drop__input');

    await act(async () => {
      fireEvent.dragEnter(dropzone);
    });

    await waitFor(() => {
      expect(screen.getByText('Drop files here')).toBeInTheDocument();
    });
  });

  it('should call onDrop with correct files when files are dropped', async () => {
    const files = [createMockFile('dropped.txt', 'dropped content')];
    render(<DragAndDrop onDrop={mockOnDrop} />);

    const dropzone = screen.getByTestId('drag-drop__input');
    const dropEvent = createDragEvent(files);

    await act(async () => {
      fireEvent.drop(dropzone, dropEvent);
    });

    await waitFor(() => {
      // react-dropzone calls onDrop with (acceptedFiles, fileRejections, event)
      expect(mockOnDrop).toHaveBeenCalledWith(files, [], expect.any(Object));
      expect(mockOnDrop).toHaveBeenCalledTimes(1);
    });
  });

  it('should handle multiple files being dropped', async () => {
    const files = [
      createMockFile('file1.pdf', 'pdf content', 'application/pdf'),
      createMockFile('file2.jpg', 'image content', 'image/jpeg'),
      createMockFile('file3.txt', 'text content', 'text/plain')
    ];
    render(<DragAndDrop onDrop={mockOnDrop} />);

    const dropzone = screen.getByTestId('drag-drop__input');
    const dropEvent = createDragEvent(files);

    await act(async () => {
      fireEvent.drop(dropzone, dropEvent);
    });

    await waitFor(() => {
      // react-dropzone calls onDrop with (acceptedFiles, fileRejections, event)
      expect(mockOnDrop).toHaveBeenCalledWith(files, [], expect.any(Object));
      expect(mockOnDrop).toHaveBeenCalledTimes(1);
    });
  });

  it('should return to normal state after drag ends', async () => {
    render(<DragAndDrop onDrop={mockOnDrop} />);

    const dropzone = screen.getByTestId('drag-drop__input');

    await act(async () => {
      fireEvent.dragEnter(dropzone);
    });

    expect(screen.getByText('Drop files here')).toBeInTheDocument();

    await act(async () => {
      fireEvent.dragLeave(dropzone);
    });

    await waitFor(() => {
      expect(screen.queryByText('Drop files here')).not.toBeInTheDocument();
      expect(screen.getByText('Browse files or drag and drop files')).toBeInTheDocument();
    });
  });

  it('should not call onDrop when disabled and files are dropped', async () => {
    const files = [createMockFile()];
    render(<DragAndDrop onDrop={mockOnDrop} disabled />);

    const dropzone = screen.getByTestId('drag-drop__input');
    const dropEvent = createDragEvent(files);

    await act(async () => {
      fireEvent.drop(dropzone, dropEvent);
    });

    await waitFor(() => {
      expect(mockOnDrop).not.toHaveBeenCalled();
    });
  });

  it('should not show drag state when disabled', async () => {
    render(<DragAndDrop onDrop={mockOnDrop} disabled />);

    const dropzone = screen.getByTestId('drag-drop__input');

    await act(async () => {
      fireEvent.dragEnter(dropzone);
    });

    // Should not show drag message when disabled
    expect(screen.queryByText('Drop files here')).not.toBeInTheDocument();
  });
});
