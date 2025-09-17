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

// Main entry point for tableBrowserReact
export { default as TableBrowserPage } from './TableBrowserPage';

// Source Listing
export { default as SourcesList } from './SourceListing/SourcesList';

// Database Listing
export { default as DatabasesList } from './DatabaseListing/DatabasesList';
export { default as DatabaseProperties } from './DatabaseListing/DatabaseProperties';

// Table Listing
export { default as TablesList } from './TableListing/TablesList';

// Table Details
export { default as TableDetails } from './TableDetails/TableDetails';
export { default as Overview } from './TableDetails/OverviewTab/Overview';
export { default as DetailsProperties } from './TableDetails/DetailsTab/DetailsProperties';
export { default as DetailsSchema } from './TableDetails/DetailsTab/DetailsSchema';
export { default as Partitions } from './TableDetails/PartitionsTab/Partitions';
export { default as Privileges } from './TableDetails/PrivilegesTab/Privileges';
export { default as Queries } from './TableDetails/QueriesTab/Queries';
export { default as ViewSql } from './TableDetails/ViewSqlTab/ViewSql';
export { default as SampleGrid } from './TableDetails/SampleTab/SampleGrid';

// Shared Components
export { default as Breadcrumbs } from './sharedComponents/Breadcrumbs';
export { default as PageHeader } from './sharedComponents/PageHeader';
export { default as Toolbar } from './sharedComponents/Toolbar';
export { default as Tabs } from './sharedComponents/Tabs';
export { default as TableBrowserErrorBoundary } from './sharedComponents/TableBrowserErrorBoundary';
export { default as InlineDescriptionEditor } from './sharedComponents/InlineDescriptionEditor';
export { default as MetaDataDisplay } from './sharedComponents/MetaDataDisplay';

// Hooks
export { default as useDatabaseProperties } from './hooks/useDatabaseProperties';
export { default as useDescriptionManager } from './hooks/useDescriptionManager';
export { default as useTableBrowserController } from './hooks/useTableBrowserController';
export { default as useTableDetails } from './hooks/useTableDetails';

// Utils
export * from './utils/connector';
export * from './utils/notifier';
export * from './utils/routing';

// Types (if needed)
export type { default as TableBrowserPageProps } from './TableBrowserPage';
