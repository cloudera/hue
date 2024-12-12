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
import { render, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import DragAndDrop from './DragAndDrop';

describe('DragAndDrop', () => {
  const mockOnFilesDrop = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the initial message when not dragging and children not present', () => {
    const { getByText } = render(<DragAndDrop onDrop={mockOnFilesDrop} />);

    expect(
      getByText("Drag 'n' drop some files here, or click to select files")
    ).toBeInTheDocument();
  });

  it('should render children when provided and not dragging', () => {
    const { getByText } = render(
      <DragAndDrop onDrop={mockOnFilesDrop}>
        <div>Custom Child Element</div>
      </DragAndDrop>
    );

    expect(getByText('Custom Child Element')).toBeInTheDocument();
  });

  it('should not display the default message when children are passed', () => {
    const { queryByText, getByText } = render(
      <DragAndDrop onDrop={mockOnFilesDrop}>
        <div>Custom Child Element</div>
      </DragAndDrop>
    );

    expect(
      queryByText("Drag 'n' drop some files here, or click to select files")
    ).not.toBeInTheDocument();
    expect(getByText('Custom Child Element')).toBeInTheDocument();
  });

  it('should display the dragging message when dragging files', async () => {
    const { getByText, getByTestId } = render(<DragAndDrop onDrop={mockOnFilesDrop} />);

    await act(async () => fireEvent.dragEnter(getByTestId('drag-drop__input')));

    await waitFor(() => {
      expect(getByText('Drop files here to upload')).toBeInTheDocument();
    });
  });

  it('should call onDrop when files are dropped', async () => {
    const files = [new File(['fileContents'], 'test.txt', { type: 'text/plain' })];

    const { getByTestId } = render(<DragAndDrop onDrop={mockOnFilesDrop} />);

    const dropzone = getByTestId('drag-drop__input');

    const dropEvent = {
      dataTransfer: {
        files,
        items: files.map(file => ({
          kind: 'file',
          type: file.type,
          getAsFile: () => file
        })),
        types: ['Files']
      }
    };

    await act(async () => fireEvent.drop(dropzone, dropEvent));

    await waitFor(() => {
      expect(mockOnFilesDrop).toHaveBeenCalledTimes(1);
    });
  });
});
