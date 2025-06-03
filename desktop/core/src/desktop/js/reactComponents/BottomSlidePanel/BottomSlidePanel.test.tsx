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
import { render, fireEvent, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import BottomSlidePanel from './BottomSlidePanel';

describe('BottomSlidePanel', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    onPrimaryClick: jest.fn(),
    primaryText: 'Create',
    cancelText: 'Cancel',
    title: 'Create Folder',
    children: <div>Panel Content</div>
  };

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should render when isOpen is true', () => {
    render(<BottomSlidePanel {...defaultProps} />);
    expect(screen.getByText('Create Folder')).toBeInTheDocument();
    expect(screen.getByText('Panel Content')).toBeInTheDocument();
    expect(screen.getByText('Create')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('should not render when isOpen is false', () => {
    const { queryByText } = render(<BottomSlidePanel {...defaultProps} isOpen={false} />);
    expect(queryByText('Create Folder')).not.toBeInTheDocument();
    expect(queryByText('Panel Content')).not.toBeInTheDocument();
  });

  it('should call onPrimaryClick when primary button is clicked', () => {
    render(<BottomSlidePanel {...defaultProps} />);
    fireEvent.click(screen.getByText('Create'));
    expect(defaultProps.onPrimaryClick).toHaveBeenCalled();
  });

  it('should call onClose when cancel button is clicked', () => {
    render(<BottomSlidePanel {...defaultProps} />);
    fireEvent.click(screen.getByText('Cancel'));
    expect(defaultProps.onClose).toHaveBeenCalled();
  });

  it('should call onClose when mask is clicked and maskClosable is true', () => {
    render(<BottomSlidePanel {...defaultProps} />);
    const mask = screen.getByTestId('mask');
    fireEvent.click(mask);
    expect(defaultProps.onClose).toHaveBeenCalled();
  });

  it('should not call onClose when mask is clicked and maskClosable is false', () => {
    render(<BottomSlidePanel {...defaultProps} maskClosable={false} />);
    const mask = screen.getByTestId('mask');
    fireEvent.click(mask);
    expect(defaultProps.onClose).not.toHaveBeenCalled();
  });

  it('should call onClose on Enter or Space keydown on mask', () => {
    render(<BottomSlidePanel {...defaultProps} />);
    const mask = screen.getByTestId('mask');
    fireEvent.keyDown(mask, { key: 'Enter' });
    fireEvent.keyDown(mask, { key: ' ' });
    expect(defaultProps.onClose).toHaveBeenCalledTimes(2);
  });

  it('should apply custom className to panel', () => {
    const className = 'custom-class';
    const { container } = render(<BottomSlidePanel {...defaultProps} className={className} />);
    expect(container.querySelector('.hue-bottom-slide-panel')).toHaveClass(className);
  });

  it('should not render footer if buttons are not provided', () => {
    render(<BottomSlidePanel {...defaultProps} primaryText={undefined} cancelText={undefined} />);
    expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument();
  });
});
