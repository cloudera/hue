# Metastore (Legacy Table Browser) Functional Specification

## Overview
The Metastore application is Hue's legacy table browser, providing comprehensive database and table management capabilities for various data sources (primarily Hive, Impala, and other SQL engines). It serves as a web-based interface for exploring, managing, and interacting with database schemas, tables, partitions, and metadata.

## Core Architecture

### Backend (Django/Python)
- **App Location**: `apps/metastore/`
- **Main Files**:
  - `views.py` - Core view logic and API endpoints
  - `urls.py` - URL routing configuration
  - `models.py` - Data models (minimal, mostly uses external connectors)
  - `forms.py` - Django forms for data loading and database operations
  - `conf.py` - Configuration settings

### Frontend (JavaScript/Knockout.js/Mako Templates)
- **Templates**: `apps/metastore/src/metastore/templates/`
- **JavaScript**: `desktop/core/src/desktop/js/apps/tableBrowser/`
- **Styling**: `apps/metastore/src/metastore/static/metastore/css/metastore.css`

## Major Functional Areas

### 1. Database Management

#### Database Listing & Navigation
- **Endpoint**: `/metastore/databases/`
- **Features**:
  - Lists all available databases in the connected data source
  - Search/filter databases by name
  - Source selection dropdown (when multiple sources configured)
  - Namespace selection (for multi-cluster environments)
  - Breadcrumb navigation

#### Database Operations
- **View Database Properties**:
  - Owner information (name and type)
  - Location (HDFS path with clickable link)
  - Database parameters/properties
  - Creation metadata

- **Alter Database** (`POST /metastore/databases/{database}/alter`):
  - Modify database properties via key-value pairs
  - Requires write permissions

- **Drop Database** (`POST /metastore/databases/drop`):
  - Bulk deletion of selected databases
  - Confirmation modal with warning about cascading deletion
  - Supports both embedded and standalone modes
  - Generates DDL or executes directly

- **Create Database**:
  - Integration with table creation wizard
  - Links to Beeswax create database functionality

### 2. Table Management

#### Table Listing & Discovery
- **Endpoint**: `/metastore/tables/{database}/`
- **Features**:
  - Lists all tables and views in a database
  - Table type indicators (Table/View, Managed/External)
  - Search and filtering capabilities
  - Bulk selection for operations
  - Table statistics display (row count, file count, size)

#### Table Operations
- **View Table** - Navigate to detailed table view
- **Query Table** - Launch SQL query interface
- **Drop Tables** (`POST /metastore/tables/drop/{database}`):
  - Bulk table deletion with confirmation
  - Skip trash option
  - Embedded mode support
- **Create Tables**:
  - "New from file" - Import wizard integration
  - "New manually" - Manual table creation
  - Integration with new table creation workflow

### 3. Detailed Table View

#### Table Overview Tab
- **Table Metadata**:
  - Table name with inline editing capability
  - Table type (Managed/External, Partitioned/Non-partitioned)
  - Storage format and location
  - Creation information (owner, creation date)
  - Table statistics (files, rows, total size, last modified)

- **Column Schema**:
  - Column names, types, and comments
  - Partition key identification
  - Column statistics when available
  - Inline editing of column properties

#### Partitions Tab (for partitioned tables)
- **Partition Management**:
  - List all partitions with values and specifications
  - Partition browsing (file system integration)
  - Partition querying capabilities
  - Bulk partition operations
  - Drop partitions functionality

#### Sample Data Tab
- **Data Preview**:
  - Sample data display in tabular format
  - Configurable sample size
  - Column navigation for wide tables
  - Export capabilities

#### Relationships Tab (ERD)
- **Entity Relationship Diagram**:
  - Visual representation of table relationships
  - Join analysis and recommendations
  - Interactive navigation between related tables
  - Animated transitions between views

#### View SQL Tab (for views)
- **SQL Definition**:
  - Formatted SQL query that defines the view
  - Syntax highlighting
  - Copy/edit capabilities

#### Details Tab
- **Raw Metadata**:
  - Complete table properties
  - Storage details
  - Serde information
  - All available metadata in structured format

#### Privileges Tab
- **Security Information**:
  - Table-level permissions
  - Integration with Sentry/Ranger
  - User and group access controls

### 4. Data Import/Export

#### Import Data Modal
- **File Upload Interface**:
  - Path selection with file browser integration
  - Partition value specification for partitioned tables
  - Overwrite option
  - Progress tracking and status updates
  - Note: Import is visible only for compatible sources — table details are loaded, the entry is not a view, the dialect is not Spark SQL, and for Hive it must not be a transactional table.

#### Export Capabilities
- **Query Integration**:
  - Direct SQL query generation
  - Integration with notebook/editor
  - Result export options

### 5. Search & Discovery

#### Global Search
- **Multi-level Search**:
  - Database name filtering
  - Table name filtering
  - Column name searching
  - Metadata search integration

#### Catalog Integration
- **Navigator Integration** (when enabled):
  - Rich metadata from Apache Atlas/Navigator
  - Tags and classifications
  - Lineage information
  - Data governance features

### 6. Query Integration

#### SQL Analyzer Integration
- **Query Recommendations**:
  - Popular queries for tables
  - Query complexity analysis
  - Performance insights
  - Compatibility indicators (Hive/Impala)

#### Editor Integration
- **Seamless Transitions**:
  - "Query" button launches editor with context
  - Table/column name insertion
  - Query history integration

## Technical Features

### Multi-Source Support
- **Connector Architecture**:
  - Hive integration
  - Impala support
  - Spark SQL compatibility
  - Generic JDBC connectors

### Permission System
- **Access Control**:
  - Read-only mode support
  - Write permission checking
  - Integration with Hue's user management
  - Granular operation permissions

### Responsive Design
- **UI Adaptability**:
  - Embeddable mode for integration
  - Responsive layouts
  - Mobile-friendly interfaces
  - Customizable themes

### Performance Optimizations
- **Lazy Loading**:
  - Progressive data loading
  - Pagination support
  - Caching mechanisms
  - Optimized metadata retrieval

## Configuration Options

### Settings (`metastore/conf.py`)
- `FORCE_HS2_METADATA` - Force HiveServer2 metadata usage
- `SHOW_TABLE_ERD` - Enable/disable ERD functionality
- `ENABLE_NEW_CREATE_TABLE` - Toggle new table creation workflow

### Integration Settings
- Navigator/Atlas integration toggles
- SQL Analyzer configuration
- Multi-cluster support settings
- Security integration options

## User Workflows

### Common Database Administration Tasks
1. **Database Exploration**:
   - Navigate to Metastore
   - Select appropriate source/namespace
   - Browse database list
   - Examine database properties

2. **Table Discovery**:
   - Enter database view
   - Use search/filter to find tables
   - Examine table metadata
   - Preview sample data

3. **Data Loading**:
   - Navigate to target table
   - Click Import button
   - Configure file path and options
   - Monitor loading progress

4. **Schema Management**:
   - View table structure
   - Modify table/column properties
   - Manage partitions
   - Drop obsolete objects

### Advanced Features
1. **Relationship Analysis**:
   - Access ERD view
   - Analyze table joins
   - Navigate related tables
   - Export relationship diagrams

2. **Query Development**:
   - Browse table structure
   - Launch query editor
   - Utilize query suggestions
   - Access query history

## Integration Points

### With Other Hue Apps
- **Notebook/Editor**: Query execution and development
- **File Browser**: File system navigation and data import
- **Job Browser**: Query execution monitoring
- **Security**: Permission management and access control

### External Systems
- **Hadoop Ecosystem**: HDFS, Hive, Impala, Spark
- **Metadata Systems**: Apache Atlas, Cloudera Navigator
- **Security**: Apache Sentry, Apache Ranger
- **Storage**: Various file formats and storage systems

## Complete API Reference

### Database Endpoints
- `GET /metastore/` - Redirects to default tables view
- `GET /metastore/databases/` - List all databases with search/filter support
- `POST /metastore/databases/drop/` - Drop selected databases (bulk operation)
- `POST /metastore/databases/{database}/alter` - Alter database properties
- `GET /metastore/databases/{database}/metadata` - Get database metadata

### Table Endpoints
- `GET /metastore/tables/` - List tables in default database
- `GET /metastore/tables/{database}/` - List tables in specific database
- `POST /metastore/tables/drop/{database}` - Drop selected tables (bulk operation)
- `GET /metastore/table/{database}/{table}/` - Describe table (detailed view)
- `POST /metastore/table/{database}/{table}/alter` - Alter table properties
- `GET /metastore/table/{database}/{table}/metadata` - Get table metadata
- `GET|POST /metastore/table/{database}/{table}/load` - Load data into table
- `GET /metastore/table/{database}/{table}/read` - Read table data (deprecated, links to Beeswax)
- `GET /metastore/table/{database}/{table}/queries` - Get related queries for table

### Partition Endpoints
- `GET|POST /metastore/table/{database}/{table}/partitions/` - List/filter partitions
- `GET /metastore/table/{database}/{table}/partitions/{partition_spec}/read` - Read partition data (deprecated)
- `GET /metastore/table/{database}/{table}/partitions/{partition_spec}/browse` - Browse partition files (links to File Browser)
- `POST /metastore/table/{database}/{table}/partitions/drop` - Drop selected partitions

### Column Endpoints
- `POST /metastore/table/{database}/{table}/alter_column` - Alter column properties

### Response Formats
- **HTML**: Full page renders with Mako templates
- **JSON**: API responses with `format=json` parameter
- **Embedded**: Special handling for `is_embeddable=true` parameter

## Detailed UI Components

### Navigation Components
- **Breadcrumb Navigation**: Dynamic breadcrumbs with editable table names
- **Source Selector**: Dropdown for multiple data sources (Hive, Impala, etc.)
- **Namespace Selector**: Multi-cluster environment support
- **Search/Filter**: Real-time filtering across databases and tables

### Data Display Components
- **Database List**: Sortable table with metadata and actions
- **Table List**: Grid view with type indicators, statistics, and bulk operations
- **Column Schema**: Expandable table with inline editing capabilities
- **Partition Browser**: Hierarchical view with filtering and bulk operations
- **Sample Data Viewer**: Paginated table with column navigation aids

### Interactive Elements
- **Inline Editors**: Click-to-edit for table names, comments, and descriptions
- **Modal Dialogs**: Confirmation dialogs for destructive operations
- **Progress Indicators**: Loading spinners and progress bars for long operations
- **Context Menus**: Right-click actions for tables and databases
- **Bulk Selection**: Checkbox-based multi-selection with action bars

### Integration Links
- **Query Editor**: "Query" buttons launch Notebook/Editor with table context
- **File Browser**: "Browse" links open File Browser at table/partition locations  
- **Import Wizard**: "New" buttons link to table creation workflows
- **Job Browser**: Background job monitoring links for DDL operations

### Button and Tab Visibility Rules
- **Query vs Browse Data button (header)**:
  - If `USE_NEW_EDITOR` is true: show Query button (launches editor with context)
  - Else: show Browse Data link to legacy read endpoint
- **Import button**:
  - Visible only when table details are loaded AND entry is not a view AND dialect is not Spark SQL AND (for Hive) table is not transactional
- **Drop (single table) button**:
  - Visible only if user has write access
- **Refresh button**:
  - Always visible; shows spinner when `refreshing` is true
- **Tables action bar (database view)**:
  - View and Query require exactly one selected table
  - Drop requires at least one selected table and write access
  - New table buttons shown when write access; link destination depends on `ENABLE_NEW_CREATE_TABLE` and embedding (see below)
- **Databases action bar**:
  - Drop requires selection and write access
  - New database shown when write access; link destination depends on embedding and toggles
- **Tabs on table details**:
  - Partitions: shown only if `partition_keys.length > 0`
  - View SQL: shown only if entry is a view
  - ERD: shown only if `SHOW_TABLE_ERD` is enabled
  - Privileges: shown only if `appConfig.browser.interpreter_names` contains `security`
  - Queries: shown only when SQL Analyzer is enabled
- **Description editing**:
  - Inline editing enabled unless `HAS_READ_ONLY_CATALOG` is set; otherwise read-only display

### Embedded vs Standalone Differences
- **Headers/Assist**: In embedded mode the common header and assist panel are hidden
- **Create/Drop/Load execution**:
  - Embedded mode uses "generate DDL only" and submits tasks to Notebook, returning JSON job payloads (no redirect)
  - Standalone mode executes operations via Beeswax/redirects to watch pages
- **Create links**:
  - Embedded: New Table/Database links point to `indexer:importer_prefill` with connector/namespace/compute params
  - Standalone with legacy flow: New Table links go to Beeswax create/import wizard
- **Forms**:
  - Embedded forms include hidden `is_embeddable`, `start_time`, `namespace`, `cluster`, and `source_type` fields

### Assist Panel
- In non-embedded mode, a left Assist panel can be toggled; shows SQL assist with stats and supports split resizing

### Breadcrumbs Editing
- Table breadcrumb is inline-editable; activates a `hiveChooser` that lets users change the table path (database and table) within the current namespace/compute; on change, navigates to the selected entry and exits edit mode

### Deprecated Behaviors
- `read_table` and `read_partition` endpoints are deprecated; modern flows use the Query editor or direct file browsing via generated links

### JSON Response Shapes (selected)
- `GET /metastore/tables/{database}?format=json`:
  - `{ status: 0, database_meta, tables, table_names, search_filter }`
- `POST /metastore/table/{database}/{table}/metadata`:
  - `{ status: 0, data: { comment, hdfs_link, is_view } }`
- `GET /metastore/table/{database}/{table}?format=json` (describe table):
  - `{ status: 0, name, partition_keys, cols, path_location, hdfs_link, comment, is_view, properties, details, stats }`
- `GET|POST /metastore/table/{db}/{table}/partitions?format=json`:
  - `{ partition_keys_json: string[], partition_values_json: Array<{ columns: string[], partitionSpec, readUrl, browseUrl, notebookUrl }> }`

## Permission Model

### Access Levels
- **Read-Only**: View databases, tables, and metadata
- **Write Access**: All read permissions plus:
  - Create/drop databases and tables
  - Alter table/column properties
  - Load data into tables
  - Drop partitions

### Permission Checks
- `has_write_access()` function checks user permissions
- `@check_has_write_access_permission` decorator on write operations
- Integration with Hue's role-based access control
- Granular permissions via `user.has_hue_permission(action="write", app="metastore")`

## Configuration & Customization

### Feature Toggles
- `SHOW_TABLE_ERD` - Enable/disable relationship diagrams
- `ENABLE_NEW_CREATE_TABLE` - Use new vs. legacy table creation
- `FORCE_HS2_METADATA` - Force HiveServer2 metadata retrieval
- `LIST_PARTITIONS_LIMIT` - Limit number of partitions displayed

### Integration Flags
- `HAS_SQL_ANALYZER` - Enable query analysis features
- `HAS_CATALOG` - Enable Navigator/Atlas integration
- `HAS_MULTI_CLUSTER` - Enable multi-cluster support
- `USE_NEW_EDITOR` - Use new vs. legacy query editor

### Appearance Settings
- Embeddable mode for iframe integration
- Custom banner support
- Responsive layout adjustments
- Theme customization support

## Data Flow & State Management

### Frontend Architecture
- **Knockout.js MVVM**: Reactive data binding and UI updates
- **Observable Patterns**: Real-time UI updates from data changes
- **Component System**: Reusable UI components with parameters
- **Event System**: PubSub for cross-component communication

### Backend Integration
- **Django Views**: Server-side rendering and API endpoints
- **Database Connectors**: Pluggable backend for different data sources
- **Caching Layer**: Metadata caching for performance
- **Error Handling**: Comprehensive exception handling with user feedback

### State Persistence
- **URL Parameters**: Deep linking and browser history support
- **Session Storage**: User preferences and view state
- **Local Storage**: Performance optimizations and offline support

## Error Handling & User Experience

### Error Management
- Graceful degradation when services unavailable
- Comprehensive error messages with context
- Retry mechanisms for transient failures
- Fallback options for missing features

### User Guidance
- Contextual help and tooltips
- Progressive disclosure of advanced features
- Keyboard shortcuts and accessibility
- Responsive feedback for all operations

### Performance Considerations
- Lazy loading of large datasets
- Pagination for table and partition lists
- Debounced search/filter inputs
- Optimized metadata retrieval strategies
