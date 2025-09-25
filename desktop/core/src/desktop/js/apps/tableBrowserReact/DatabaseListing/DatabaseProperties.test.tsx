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
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import DatabasePropertiesComponent, { DatabaseProperties } from './DatabaseProperties';

// Mock the MetaDataDisplay component
jest.mock('../sharedComponents/MetaDataDisplay', () => {
  return function MockMetaDataDisplay({ groups }: { groups: any[] }) {
    return (
      <div data-testid="metadata-display">
        {groups.map((group, groupIndex) =>
          group.items.map((item: any, itemIndex: number) => (
            <div key={`${groupIndex}-${itemIndex}`} data-testid={`metadata-item-${item.key}`}>
              <div data-testid={`metadata-label-${item.key}`}>{item.label}</div>
              <div data-testid={`metadata-value-${item.key}`}>{item.value}</div>
            </div>
          ))
        )}
      </div>
    );
  };
});

// Mock the Loading component
jest.mock('cuix/dist/components/Loading', () => {
  return function MockLoading({
    spinning,
    children
  }: {
    spinning: boolean;
    children: React.ReactNode;
  }) {
    return (
      <div data-testid="loading" data-spinning={spinning}>
        {children}
      </div>
    );
  };
});

describe('DatabasePropertiesComponent', () => {
  const defaultProps = {
    loading: false
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic rendering', () => {
    it('renders empty component when no properties', () => {
      render(<DatabasePropertiesComponent {...defaultProps} />);
      expect(screen.getByTestId('loading')).toBeInTheDocument();
      expect(screen.getByTestId('loading')).toHaveAttribute('data-spinning', 'false');
    });

    it('shows loading state', () => {
      render(<DatabasePropertiesComponent {...defaultProps} loading={true} />);
      expect(screen.getByTestId('loading')).toHaveAttribute('data-spinning', 'true');
    });

    it('renders with basic properties', () => {
      const properties: DatabaseProperties = {
        owner_name: 'test_user',
        owner_type: 'USER',
        location: '/test/location'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      expect(screen.getByTestId('metadata-display')).toBeInTheDocument();
      expect(screen.getByTestId('metadata-item-owner')).toBeInTheDocument();
      expect(screen.getByTestId('metadata-item-location')).toBeInTheDocument();
    });
  });

  describe('Parameters parsing', () => {
    it('parses simple parameters correctly', () => {
      const properties: DatabaseProperties = {
        parameters: '{comment=Simple test comment, type=DATABASE}'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const parametersValue = screen.getByTestId('metadata-value-parameters');
      expect(parametersValue).toBeInTheDocument();

      // Check that parameters are rendered as a list
      expect(
        parametersValue.querySelector('.hue-database-properties__parameters-list')
      ).toBeInTheDocument();

      // Check individual parameter items
      const parameterItems = parametersValue.querySelectorAll(
        '.hue-database-properties__parameter-item'
      );
      expect(parameterItems).toHaveLength(2);

      // Check first parameter
      expect(parameterItems[0]).toHaveTextContent('comment:');
      expect(parameterItems[0]).toHaveTextContent('Simple test comment');

      // Check second parameter
      expect(parameterItems[1]).toHaveTextContent('type:');
      expect(parameterItems[1]).toHaveTextContent('DATABASE');
    });

    it('handles complex parameters with long values', () => {
      const properties: DatabaseProperties = {
        parameters:
          '{comment=This is also a very long description, This is also a very long description, This is also a very long description, owner=admin_user}'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const parametersValue = screen.getByTestId('metadata-value-parameters');
      const parameterItems = parametersValue.querySelectorAll(
        '.hue-database-properties__parameter-item'
      );

      // Note: The parsing logic will split on commas, so this creates multiple parameters
      // The first parameter will be "comment=This is also a very long description"
      // The subsequent parts will be treated as separate parameters without proper key=value format
      // Only valid key=value pairs will be displayed
      expect(parameterItems.length).toBeGreaterThanOrEqual(1);

      // Check that the comment parameter is properly displayed (only the first part)
      expect(parameterItems[0]).toHaveTextContent('comment:');
      expect(parameterItems[0]).toHaveTextContent('This is also a very long description');

      // Check that owner parameter is found (it should be the last valid one)
      const ownerItem = Array.from(parameterItems).find(item =>
        item.textContent?.includes('owner:')
      );
      expect(ownerItem).toBeDefined();
      expect(ownerItem).toHaveTextContent('admin_user');
    });

    it('handles parameters with nested braces', () => {
      const properties: DatabaseProperties = {
        parameters: '{config={nested=value, another=test}, simple=basic}'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const parametersValue = screen.getByTestId('metadata-value-parameters');
      const parameterItems = parametersValue.querySelectorAll(
        '.hue-database-properties__parameter-item'
      );
      expect(parameterItems).toHaveLength(2);

      // Check nested parameter
      expect(parameterItems[0]).toHaveTextContent('config:');
      expect(parameterItems[0]).toHaveTextContent('{nested=value, another=test}');

      // Check simple parameter
      expect(parameterItems[1]).toHaveTextContent('simple:');
      expect(parameterItems[1]).toHaveTextContent('basic');
    });

    it('handles single parameter', () => {
      const properties: DatabaseProperties = {
        parameters: '{comment=Single parameter value}'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const parametersValue = screen.getByTestId('metadata-value-parameters');
      const parameterItems = parametersValue.querySelectorAll(
        '.hue-database-properties__parameter-item'
      );
      expect(parameterItems).toHaveLength(1);

      expect(parameterItems[0]).toHaveTextContent('comment:');
      expect(parameterItems[0]).toHaveTextContent('Single parameter value');
    });

    it('handles empty parameters', () => {
      const properties: DatabaseProperties = {
        parameters: '{}'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const parametersValue = screen.getByTestId('metadata-value-parameters');
      expect(parametersValue).toHaveTextContent('None');
      expect(
        parametersValue.querySelector('.hue-database-properties__property-empty')
      ).toBeInTheDocument();
    });

    it('handles malformed parameters gracefully', () => {
      const properties: DatabaseProperties = {
        parameters: 'not-valid-format'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const parametersValue = screen.getByTestId('metadata-value-parameters');
      // Should show "None" since no valid key=value pairs are found
      expect(parametersValue).toHaveTextContent('None');
      expect(
        parametersValue.querySelector('.hue-database-properties__property-empty')
      ).toBeInTheDocument();
    });

    it('falls back to raw display on parsing error', () => {
      // Mock console.error to avoid noise in test output
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      // Create a mock that will cause the parsing to throw an error
      const originalSubstring = String.prototype.substring;
      const mockSubstring = jest.fn().mockImplementation(function (this: string, ...args) {
        if (this.includes('error-trigger')) {
          throw new Error('Parsing error');
        }
        return originalSubstring.apply(this, args);
      });
      String.prototype.substring = mockSubstring;

      const properties: DatabaseProperties = {
        parameters: '{error-trigger=value}'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const parametersValue = screen.getByTestId('metadata-value-parameters');
      // Should fallback to original display
      expect(
        parametersValue.querySelector('.hue-database-properties__parameters')
      ).toBeInTheDocument();
      expect(parametersValue).toHaveTextContent('{error-trigger=value}');

      // Restore original methods
      String.prototype.substring = originalSubstring;
      consoleSpy.mockRestore();
    });

    it('handles parameters without equals sign', () => {
      const properties: DatabaseProperties = {
        parameters: '{validkey=validvalue, invalidkey, anothervalid=test}'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const parametersValue = screen.getByTestId('metadata-value-parameters');
      const parameterItems = parametersValue.querySelectorAll(
        '.hue-database-properties__parameter-item'
      );
      // Should only parse valid key=value pairs
      expect(parameterItems).toHaveLength(2);

      expect(parameterItems[0]).toHaveTextContent('validkey:');
      expect(parameterItems[0]).toHaveTextContent('validvalue');

      expect(parameterItems[1]).toHaveTextContent('anothervalid:');
      expect(parameterItems[1]).toHaveTextContent('test');
    });

    it('handles parameters with special characters', () => {
      const properties: DatabaseProperties = {
        parameters:
          '{path=/hdfs/path/with/special-chars_123, url=https://example.com:8080/path?param=value}'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const parametersValue = screen.getByTestId('metadata-value-parameters');
      const parameterItems = parametersValue.querySelectorAll(
        '.hue-database-properties__parameter-item'
      );
      expect(parameterItems).toHaveLength(2);

      expect(parameterItems[0]).toHaveTextContent('path:');
      expect(parameterItems[0]).toHaveTextContent('/hdfs/path/with/special-chars_123');

      expect(parameterItems[1]).toHaveTextContent('url:');
      expect(parameterItems[1]).toHaveTextContent('https://example.com:8080/path?param=value');
    });
  });

  describe('Owner display', () => {
    it('displays owner with type', () => {
      const properties: DatabaseProperties = {
        owner_name: 'test_user',
        owner_type: 'USER'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const ownerValue = screen.getByTestId('metadata-value-owner');
      expect(ownerValue).toHaveTextContent('test_user');
      expect(ownerValue).toHaveTextContent('(USER)');
    });

    it('displays owner without type', () => {
      const properties: DatabaseProperties = {
        owner_name: 'test_user'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const ownerValue = screen.getByTestId('metadata-value-owner');
      expect(ownerValue).toHaveTextContent('test_user');
      expect(ownerValue).not.toHaveTextContent('(');
    });

    it('displays None for missing owner', () => {
      const properties: DatabaseProperties = {};

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const ownerValue = screen.getByTestId('metadata-value-owner');
      expect(ownerValue).toHaveTextContent('None');
      expect(
        ownerValue.querySelector('.hue-database-properties__property-empty')
      ).toBeInTheDocument();
    });
  });

  describe('Location display', () => {
    it('displays location with HDFS link', () => {
      const properties: DatabaseProperties = {
        location: '/test/location',
        hdfs_link: 'http://namenode:9870/explorer.html#/test/location'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const locationValue = screen.getByTestId('metadata-value-location');
      const link = locationValue.querySelector('a');
      expect(link).toBeInTheDocument();
      expect(link).toHaveAttribute('href', 'http://namenode:9870/explorer.html#/test/location');
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('displays location as text when no HDFS link', () => {
      const properties: DatabaseProperties = {
        location: '/test/location'
      };

      render(<DatabasePropertiesComponent {...defaultProps} properties={properties} />);

      const locationValue = screen.getByTestId('metadata-value-location');
      expect(locationValue).toHaveTextContent('/test/location');
      expect(locationValue.querySelector('a')).not.toBeInTheDocument();
    });
  });
});
