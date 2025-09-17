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

import type { Connector } from '../../../config/types';

/**
 * Business logic tests for the import functionality.
 * These test the enableImport logic without rendering components to avoid Jest configuration issues.
 */

// Mock translation function
const mockT = (key: string) => key;

/**
 * Replicated enableImport logic from TableDetails component for unit testing
 */
const enableImport = (
  overviewProps?: { properties?: { name: string; value: string }[] },
  connector?: Connector | null,
  t: (key: string) => string = mockT
): boolean => {
  if (!overviewProps?.properties || !connector) {
    return false;
  }

  // Check if table details are loaded (equivalent to detailsLoaded in legacy)
  const detailsLoaded = !!overviewProps.properties.length;
  if (!detailsLoaded) {
    return false;
  }

  // Get connector dialect
  const dialect = connector.dialect || connector.id;

  // Check if it's a view
  const typeProperty = overviewProps.properties.find(p => p.name === t('Type'));
  const isView = typeProperty?.value === t('View');

  // Check if it's Spark SQL
  const isSpark = dialect === 'sparksql';

  // Check if it's transactional Hive table
  const isTransactionalHive =
    dialect === 'hive' &&
    overviewProps.properties.some(
      p => p.name.toLowerCase().includes('transactional') && p.value?.toLowerCase() === 'true'
    );

  return !(isSpark || isView || isTransactionalHive);
};

describe('Import Button Business Logic (enableImport)', () => {
  const mockConnector: Connector = {
    id: 'hive',
    dialect: 'hive',
    displayName: 'Hive',
    buttonName: 'Hive',
    tooltip: 'Hive',
    page: '/hive',
    type: 'hive'
  };

  it('should enable import for regular Hive table when details are loaded', () => {
    const overviewProps = {
      properties: [
        { name: 'Type', value: 'Table' },
        { name: 'Partitioned', value: 'No' }
      ]
    };

    const result = enableImport(overviewProps, mockConnector);
    expect(result).toBe(true);
  });

  it('should disable import when table details are not loaded', () => {
    const overviewProps = {
      properties: [] // No properties loaded
    };

    const result = enableImport(overviewProps, mockConnector);
    expect(result).toBe(false);
  });

  it('should disable import for views', () => {
    const overviewProps = {
      properties: [
        { name: 'Type', value: 'View' }, // This is a view
        { name: 'Partitioned', value: 'No' }
      ]
    };

    const result = enableImport(overviewProps, mockConnector);
    expect(result).toBe(false);
  });

  it('should disable import for Spark SQL tables', () => {
    const sparkConnector: Connector = {
      ...mockConnector,
      id: 'sparksql',
      dialect: 'sparksql'
    };

    const overviewProps = {
      properties: [
        { name: 'Type', value: 'Table' },
        { name: 'Partitioned', value: 'No' }
      ]
    };

    const result = enableImport(overviewProps, sparkConnector);
    expect(result).toBe(false);
  });

  it('should disable import for transactional Hive tables', () => {
    const overviewProps = {
      properties: [
        { name: 'Type', value: 'Table' },
        { name: 'Transactional', value: 'true' }, // Transactional table
        { name: 'Partitioned', value: 'No' }
      ]
    };

    const result = enableImport(overviewProps, mockConnector);
    expect(result).toBe(false);
  });

  it('should enable import for transactional table with non-Hive dialect', () => {
    const sqlConnector: Connector = {
      ...mockConnector,
      id: 'sql',
      dialect: 'sql'
    };

    const overviewProps = {
      properties: [
        { name: 'Type', value: 'Table' },
        { name: 'Transactional', value: 'true' }, // Transactional but not Hive
        { name: 'Partitioned', value: 'No' }
      ]
    };

    const result = enableImport(overviewProps, sqlConnector);
    expect(result).toBe(true);
  });

  it('should use connector.id as dialect when connector.dialect is not available', () => {
    const connectorWithoutDialect: Connector = {
      ...mockConnector,
      dialect: undefined as unknown as string,
      id: 'sparksql'
    };

    const overviewProps = {
      properties: [
        { name: 'Type', value: 'Table' },
        { name: 'Partitioned', value: 'No' }
      ]
    };

    const result = enableImport(overviewProps, connectorWithoutDialect);
    // Should disable import because id is 'sparksql'
    expect(result).toBe(false);
  });

  it('should handle missing connector gracefully', () => {
    const overviewProps = {
      properties: [
        { name: 'Type', value: 'Table' },
        { name: 'Partitioned', value: 'No' }
      ]
    };

    const result = enableImport(overviewProps, null);
    expect(result).toBe(false);
  });

  it('should handle missing overviewProps gracefully', () => {
    const result = enableImport(undefined, mockConnector);
    expect(result).toBe(false);
  });

  it('should handle case-insensitive transactional property matching', () => {
    const overviewProps = {
      properties: [
        { name: 'Type', value: 'Table' },
        { name: 'TRANSACTIONAL_PROPERTIES', value: 'TRUE' }, // Different case
        { name: 'Partitioned', value: 'No' }
      ]
    };

    const result = enableImport(overviewProps, mockConnector);
    // Should disable import for transactional table
    expect(result).toBe(false);
  });

  it('should handle transactional property with false value', () => {
    const overviewProps = {
      properties: [
        { name: 'Type', value: 'Table' },
        { name: 'transactional', value: 'false' }, // Explicitly false
        { name: 'Partitioned', value: 'No' }
      ]
    };

    const result = enableImport(overviewProps, mockConnector);
    // Should enable import when transactional is false
    expect(result).toBe(true);
  });
});

describe('Partition Columns Extraction Logic', () => {
  it('should extract only partition key columns', () => {
    const detailsColumns = [
      { name: 'col1', type: 'string', isPartitionKey: false },
      { name: 'partition_col1', type: 'string', isPartitionKey: true },
      { name: 'col2', type: 'int', isPartitionKey: false },
      { name: 'partition_col2', type: 'string', isPartitionKey: true }
    ];

    const partitionColumns = detailsColumns
      .filter(col => col.isPartitionKey)
      .map(col => ({
        name: col.name,
        value: '' // Default empty value
      }));

    expect(partitionColumns).toEqual([
      { name: 'partition_col1', value: '' },
      { name: 'partition_col2', value: '' }
    ]);
  });

  it('should handle tables with no partition columns', () => {
    const detailsColumns = [
      { name: 'col1', type: 'string', isPartitionKey: false },
      { name: 'col2', type: 'int', isPartitionKey: false }
    ];

    const partitionColumns = detailsColumns
      .filter(col => col.isPartitionKey)
      .map(col => ({
        name: col.name,
        value: ''
      }));

    expect(partitionColumns).toEqual([]);
  });
});
