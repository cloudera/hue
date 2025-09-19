
# Table Browser Migration Checklist
*Verification checklist for React Table Browser vs Legacy Metastore functionality*

## Database Management

### Database Listing & Navigation
- [ ] Lists all available databases in the connected data source
- [ ] Search/filter databases by name (real-time filtering)
- [ ] Source selection dropdown (when multiple sources configured)
- [ ] Namespace selection (for multi-cluster environments)
- [ ] Breadcrumb navigation with database context
- [ ] Database metadata display (owner, location, parameters)

### Database Operations
- [ ] **View Database Properties**:
  - [ ] Owner information (name and type)
  - [ ] Location (HDFS path with clickable link to File Browser)
  - [ ] Database parameters/properties display
  - [ ] Creation metadata

- [ ] **Alter Database** (`POST /metastore/databases/{database}/alter`):
  - [ ] Modify database properties via key-value pairs
  - [ ] Requires write permissions check
  - [ ] JSON response handling

- [ ] **Drop Database** (`POST /metastore/databases/drop`):
  - [ ] Bulk deletion of selected databases
  - [ ] Confirmation modal with cascading deletion warning
  - [ ] Embedded mode: generates DDL and submits to Notebook
  - [ ] Standalone mode: executes directly via Beeswax redirect
  - [ ] Form includes hidden fields for embedded mode

- [ ] **Create Database**:
  - [ ] Integration with table creation wizard
  - [ ] Links to appropriate creation flow (Beeswax vs Importer)
  - [ ] Conditional based on `ENABLE_NEW_CREATE_TABLE` setting

## Table Management

### Table Listing & Discovery
- [ ] Lists all tables and views in a database
- [ ] Table type indicators (Table/View, Managed/External, Partitioned)
- [ ] Iceberg table indicators (snowflake icon)
- [ ] Search and filtering capabilities
- [ ] Bulk selection for operations (checkbox-based)
- [ ] Table statistics display (row count, file count, size)
- [ ] Loading states and error handling

### Table Operations
- [ ] **View Table** - Navigate to detailed table view
- [ ] **Query Table** - Launch SQL query interface with table context
- [ ] **Drop Tables** (`POST /metastore/tables/drop/{database}`):
  - [ ] Bulk table deletion with confirmation modal
  - [ ] Skip trash option
  - [ ] Embedded mode support (DDL generation)
  - [ ] Standalone mode (Beeswax redirect)
- [ ] **Create Tables**:
  - [ ] "New from file" - Import wizard integration
  - [ ] "New manually" - Manual table creation
  - [ ] Integration with new table creation workflow
  - [ ] Conditional links based on embedding and feature flags

## Detailed Table View

### Table Header Actions
- [ ] **Query vs Browse Data button**:
  - [ ] If `USE_NEW_EDITOR` is true: Query button (launches editor)
  - [ ] Else: Browse Data link to legacy read endpoint
- [ ] **Import button**:
  - [ ] Visible only for compatible sources (not Spark, not views, not transactional Hive)
  - [ ] Requires table details loaded
- [ ] **Drop button**:
  - [ ] Visible only with write access
  - [ ] Single table confirmation modal
- [ ] **Refresh button**:
  - [ ] Always visible
  - [ ] Shows spinner when refreshing

### Table Overview Tab
- [ ] **Table Metadata**:
  - [ ] Table name with inline editing capability
  - [ ] Table type (Managed/External, Partitioned/Non-partitioned)
  - [ ] Storage format and location with clickable HDFS link
  - [ ] Creation information (owner, creation date)
  - [ ] Table statistics (files, rows, total size, last modified)
  - [ ] Statistics refresh capability (for non-partitioned tables)
  - [ ] Accuracy warnings for statistics

- [ ] **Column Schema**:
  - [ ] Column names, types, and comments
  - [ ] Partition key identification and display
  - [ ] Column statistics when available
  - [ ] Inline editing of column properties (if supported)

- [ ] **Description Editing**:
  - [ ] Inline editing unless `HAS_READ_ONLY_CATALOG` is set
  - [ ] Multi-line support with expand/collapse
  - [ ] Navigator integration for rich metadata

### Partitions Tab
- [ ] **Tab Visibility**: Only shown if `partition_keys.length > 0`
- [ ] **Partition Management**:
  - [ ] List all partitions with values and specifications
  - [ ] Partition column display table
  - [ ] Partition values table with bulk selection
  - [ ] Sorting support (asc/desc)
  - [ ] Filtering capabilities
  - [ ] Pagination for large partition lists (`LIST_PARTITIONS_LIMIT`)

- [ ] **Partition Operations**:
  - [ ] Query partition data (links to Notebook)
  - [ ] Browse partition files (links to File Browser) - not for Impala
  - [ ] Drop partitions (bulk operation with confirmation)
  - [ ] Embedded vs standalone execution modes

### Sample Data Tab
- [ ] **Data Preview**:
  - [ ] Sample data display in tabular format
  - [ ] Loading states and error handling
  - [ ] Column navigation aids for wide tables
  - [ ] Row numbering
  - [ ] "Did you know?" help alert for column navigation

### Relationships Tab (ERD)
- [ ] **Tab Visibility**: Only shown if `SHOW_TABLE_ERD` is enabled
- [ ] **Entity Relationship Diagram**:
  - [ ] Visual representation of table relationships
  - [ ] Join analysis and recommendations
  - [ ] Interactive navigation between related tables
  - [ ] Animated transitions (`erd-animated` class)
  - [ ] Entity click handling for table navigation
  - [ ] Loading states

### View SQL Tab
- [ ] **Tab Visibility**: Only shown if entry is a view
- [ ] **SQL Definition**:
  - [ ] Formatted SQL query that defines the view
  - [ ] Syntax highlighting with dialect support
  - [ ] Loading states

### Details Tab
- [ ] **Raw Metadata**:
  - [ ] Complete table properties in structured format
  - [ ] Storage details and Serde information
  - [ ] All available metadata display
  - [ ] Proper handling of comment sections (# prefixed)

### Privileges Tab
- [ ] **Tab Visibility**: Only shown if `appConfig.browser.interpreter_names` contains `security`
- [ ] **Security Information**:
  - [ ] Table-level permissions via Sentry component
  - [ ] Integration with Sentry/Ranger
  - [ ] Read-only mode support

### Queries Tab (SQL Analyzer)
- [ ] **Tab Visibility**: Only shown when SQL Analyzer is enabled
- [ ] **Query Analysis**:
  - [ ] Popular queries for tables
  - [ ] Query complexity analysis with color coding
  - [ ] Performance insights
  - [ ] Compatibility indicators (Hive/Impala)
  - [ ] Query character and popularity display
  - [ ] Empty state handling

## Data Import/Export

### Import Data Modal
- [ ] **Modal Trigger**: Import button with source compatibility check
- [ ] **File Upload Interface**:
  - [ ] Path selection with file browser integration
  - [ ] File chooser component with folder/file selection
  - [ ] Upload file capability
- [ ] **Partition Support**:
  - [ ] Dynamic partition value fields based on table schema
  - [ ] Partition column name and type display
- [ ] **Options**:
  - [ ] Overwrite existing data checkbox
  - [ ] Form validation and error display
- [ ] **Execution**:
  - [ ] Embedded mode: DDL generation and Notebook task submission
  - [ ] Standalone mode: Beeswax execution with redirect
  - [ ] Progress tracking and status updates
  - [ ] Error handling and display

## Navigation & UI Components

### Breadcrumb Navigation
- [ ] **Dynamic Breadcrumbs**:
  - [ ] Source/Namespace selectors (when multiple available)
  - [ ] Database > Table hierarchy
  - [ ] Editable table names with `hiveChooser` integration
  - [ ] Proper navigation on breadcrumb clicks

### Search & Discovery
- [ ] **Multi-level Search**:
  - [ ] Database name filtering
  - [ ] Table name filtering
  - [ ] Real-time search with debouncing
  - [ ] Search state persistence

### Bulk Operations
- [ ] **Selection Management**:
  - [ ] Checkbox-based multi-selection
  - [ ] Select all functionality
  - [ ] Action bar visibility based on selection
  - [ ] Clear selection capability

### Loading States & Feedback
- [ ] **Progress Indicators**:
  - [ ] Loading spinners for data fetching
  - [ ] Refresh button spinner states
  - [ ] Large spinner for initial page loads
  - [ ] Skeleton loading states where appropriate

## Integration Points

### Hue App Integration
- [ ] **Query Editor/Notebook**:
  - [ ] Query button launches editor with table context
  - [ ] Partition query links to Notebook
  - [ ] Task submission for embedded operations
- [ ] **File Browser**:
  - [ ] HDFS location links open File Browser
  - [ ] Partition browse links (not for Impala)
  - [ ] File chooser integration in import modal
- [ ] **Job Browser**:
  - [ ] Background job monitoring links for DDL operations
  - [ ] Query history integration

### Catalog Integration
- [ ] **Navigator/Atlas Integration** (when enabled):
  - [ ] Rich metadata display
  - [ ] Tags and classifications component
  - [ ] Properties component
  - [ ] Description editing integration
  - [ ] Lineage information access

### Assist Panel
- [ ] **Left Panel** (non-embedded mode):
  - [ ] Toggle assist panel visibility
  - [ ] SQL assist with navigation settings
  - [ ] Stats display capability
  - [ ] Resizable panel with split dragging

## Permission & Access Control

### Permission Checks
- [ ] **Read-Only Mode**:
  - [ ] Hide write operations when no write access
  - [ ] Display read-only indicators
  - [ ] Catalog read-only mode support
- [ ] **Write Access Features**:
  - [ ] Create/drop database buttons
  - [ ] Create/drop table buttons
  - [ ] Import data functionality
  - [ ] Alter operations
  - [ ] Drop partition capabilities

## Configuration Support

### Feature Toggles
- [ ] **ERD Support**: `SHOW_TABLE_ERD` toggle
- [ ] **Create Table Flow**: `ENABLE_NEW_CREATE_TABLE` toggle
- [ ] **Metadata Source**: `FORCE_HS2_METADATA` support
- [ ] **Partition Limits**: `LIST_PARTITIONS_LIMIT` enforcement
- [ ] **Editor Choice**: `USE_NEW_EDITOR` conditional behavior

### Integration Flags
- [ ] **SQL Analyzer**: `HAS_SQL_ANALYZER` conditional features
- [ ] **Catalog**: `HAS_CATALOG` conditional Navigator integration
- [ ] **Multi-cluster**: `HAS_MULTI_CLUSTER` namespace support
- [ ] **Read-only Catalog**: `HAS_READ_ONLY_CATALOG` editing restrictions

### Embedding Support
- [ ] **Embeddable Mode**: `is_embeddable` parameter handling
- [ ] **Header/Assist Hiding**: Proper layout in embedded mode
- [ ] **Form Modifications**: Hidden fields for embedded operations
- [ ] **Execution Differences**: DDL generation vs direct execution

## API Compatibility

### Endpoint Coverage
- [ ] **Database Endpoints**:
  - [ ] `GET /metastore/databases/` - List with search/filter
  - [ ] `POST /metastore/databases/drop/` - Bulk drop
  - [ ] `POST /metastore/databases/{database}/alter` - Alter properties
  - [ ] `GET /metastore/databases/{database}/metadata` - Get metadata

- [ ] **Table Endpoints**:
  - [ ] `GET /metastore/tables/{database}/` - List tables
  - [ ] `POST /metastore/tables/drop/{database}` - Bulk drop tables
  - [ ] `GET /metastore/table/{database}/{table}/` - Describe table
  - [ ] `POST /metastore/table/{database}/{table}/alter` - Alter table
  - [ ] `GET /metastore/table/{database}/{table}/metadata` - Get metadata
  - [ ] `GET|POST /metastore/table/{database}/{table}/load` - Load data
  - [ ] `GET /metastore/table/{database}/{table}/queries` - Related queries

- [ ] **Partition Endpoints**:
  - [ ] `GET|POST /metastore/table/{database}/{table}/partitions/` - List/filter
  - [ ] `GET /metastore/table/{database}/{table}/partitions/{spec}/browse` - Browse files
  - [ ] `POST /metastore/table/{database}/{table}/partitions/drop` - Drop partitions

- [ ] **Column Endpoints**:
  - [ ] `POST /metastore/table/{database}/{table}/alter_column` - Alter column

### Response Format Handling
- [ ] **JSON Responses**: Proper `format=json` parameter support
- [ ] **Error Handling**: Status codes and error message display
- [ ] **Embedded Responses**: Task submission JSON handling

## Error Handling & UX

### Error Management
- [ ] **Service Unavailable**: Graceful degradation
- [ ] **Error Messages**: Comprehensive context and user-friendly display
- [ ] **Retry Mechanisms**: For transient failures
- [ ] **Fallback Options**: When features are missing/disabled

### User Experience
- [ ] **Help & Guidance**: Contextual tooltips and help text
- [ ] **Progressive Disclosure**: Advanced features appropriately hidden
- [ ] **Accessibility**: Keyboard navigation and screen reader support
- [ ] **Responsive Design**: Mobile and tablet compatibility
- [ ] **Performance**: Lazy loading, debounced inputs, optimized rendering

## Migration-Specific Checks

### State Management
- [ ] **URL Parameters**: Deep linking and browser history support
- [ ] **Session Persistence**: User preferences and view state
- [ ] **Navigation State**: Proper routing between views

### Component Parity
- [ ] **Knockout.js Equivalents**: All observable patterns converted to React state
- [ ] **Mako Template Features**: All template logic converted to JSX
- [ ] **CSS Styling**: All metastore.css styles ported or replaced
- [ ] **Event Handling**: All PubSub events converted to React patterns

### Backward Compatibility
- [ ] **API Calls**: All legacy API endpoints still supported
- [ ] **URL Structure**: Existing bookmarks and links still work
- [ ] **Embedded Mode**: iFrame integration still functional
- [ ] **Configuration**: All existing feature flags respected

---

## Testing Checklist

### Functional Testing
- [ ] **Database Operations**: Create, alter, drop, browse
- [ ] **Table Operations**: Create, alter, drop, query, import
- [ ] **Partition Operations**: List, filter, query, browse, drop
- [ ] **Search & Filter**: All levels of filtering work correctly
- [ ] **Bulk Operations**: Multi-select and bulk actions

### Integration Testing
- [ ] **Cross-App Navigation**: Links to Editor, File Browser, Job Browser
- [ ] **Permission Scenarios**: Read-only and write access modes
- [ ] **Multi-Source**: Different connector types (Hive, Impala, Spark)
- [ ] **Embedded Mode**: iframe integration scenarios

### Edge Cases
- [ ] **Large Datasets**: Tables with many columns, partitions
- [ ] **Special Characters**: Database/table names with special chars
- [ ] **Network Issues**: Timeout handling and retry logic
- [ ] **Missing Features**: Graceful handling of disabled features

### Performance Testing
- [ ] **Initial Load**: Page load times comparable to legacy
- [ ] **Large Lists**: Performance with many databases/tables
- [ ] **Search Performance**: Real-time filtering responsiveness
- [ ] **Memory Usage**: No memory leaks during navigation

---

## MISSING FUNCTIONALITY ANALYSIS

Based on code review of the React Table Browser implementation, the following functionality from the legacy Metastore is **NOT YET IMPLEMENTED**:

### Critical Missing Features

#### Table Detail Tabs - Precise Visibility Conditions
- [ ] **❌ MISSING: ERD/Relationships Tab** - Only shows when `SHOW_TABLE_ERD` config is `True` (disabled by default in Hue settings)
- [x] **✅ IMPLEMENTED: View SQL Tab visibility logic** - Shows only when `catalogEntry.isView()` is true (for database views only)
- [ ] **❌ MISSING: Privileges Tab visibility logic** - Should only show when `has_navigator_enabled()` is true (Navigator/security integration enabled)
- [ ] **✅ CLARIFICATION: Queries Tab does NOT exist** - This is not a real tab in legacy UI, just content within other tabs when SQL Analyzer is enabled

#### Advanced Features
- [ ] **❌ MISSING: Statistics refresh capability** - No refresh stats button for non-partitioned tables
- [ ] **❌ MISSING: Breadcrumb table name editing** - No inline editing of table names in breadcrumbs with hiveChooser

#### Import Data Modal
- [ ] **❌ MISSING: Import visibility logic** - No `enableImport()` function checking dialect/view/transactional status
- [ ] **❌ MISSING: Dynamic partition fields** - Import modal doesn't dynamically generate partition value fields

#### Configuration & Integration
- [ ] **❌ MISSING: Feature toggle support** - No handling of `SHOW_TABLE_ERD`, `USE_NEW_EDITOR`, `HAS_SQL_ANALYZER`, etc.
- [ ] **❌ MISSING: Embedded mode differences** - No distinction between embedded vs standalone execution
- [ ] **❌ MISSING: Assist Panel integration** - No left panel with SQL assist functionality
- [ ] **❌ MISSING: Navigator/Atlas integration** - No rich metadata, tags, or properties components

### Partially Implemented Features

#### Database Operations
- [ ] **⚠️ PARTIAL: Create Database** - Uses Beeswax endpoint instead of metastore endpoint
- [ ] **⚠️ PARTIAL: Drop Database** - Uses metastore endpoint but may not handle all embedded mode scenarios

#### Table Operations  
- [ ] **⚠️ PARTIAL: Query Integration** - Basic query button but no USE_NEW_EDITOR conditional logic
- [ ] **⚠️ PARTIAL: Browse Data** - No legacy read endpoint support

#### Partition Management
- [ ] **⚠️ PARTIAL: Partition Operations** - Drop implemented but no browse/query individual partitions

#### Tab Content
- [ ] **⚠️ PARTIAL: View SQL Tab** - Basic implementation but no syntax highlighting
- [ ] **⚠️ PARTIAL: Queries Tab** - Stub implementation using top_joins instead of actual SQL Analyzer queries
- [ ] **⚠️ PARTIAL: Sample Tab** - Basic grid but no column navigation aids or "Did you know?" help

### Working Features ✅

#### Core Navigation
- [x] **✅ WORKING: Source/Database/Table navigation**
- [x] **✅ WORKING: Breadcrumb navigation**
- [x] **✅ WORKING: URL-based routing with tab support**

#### Database Listing
- [x] **✅ WORKING: Database list with search/filter**
- [x] **✅ WORKING: Database description editing**
- [x] **✅ WORKING: Database creation modal**
- [x] **✅ WORKING: Bulk database deletion**

#### Table Listing  
- [x] **✅ WORKING: Table list with search/filter**
- [x] **✅ WORKING: Table description editing**
- [x] **✅ WORKING: Bulk table deletion with skip trash**
- [x] **✅ WORKING: Table type indicators**

#### Table Details
- [x] **✅ WORKING: Overview tab with properties and stats**
- [x] **✅ WORKING: Schema display with column info**
- [x] **✅ WORKING: Partitions tab with full partition management**
- [x] **✅ WORKING: Sample data tab**
- [x] **✅ WORKING: Details tab with raw metadata**
- [x] **✅ WORKING: Import data modal (basic)**

## Priority Recommendations

### High Priority (Critical for Migration)
1. **Import visibility logic** - Essential for data loading workflows
2. **Feature toggle support** - Required for configuration compatibility  
3. **Tab visibility logic** - Needed for proper UI behavior
4. **Statistics refresh** - Data freshness management

### Medium Priority (Important for Full Parity)
1. **ERD/Relationships tab** - Advanced table analysis
2. **Embedded mode handling** - Integration scenarios
3. **Breadcrumb table name editing** - Advanced navigation
4. **Sample tab enhancements** - Column navigation aids

### Low Priority (Nice to Have)
1. **Assist panel** - Enhanced user experience  
2. **Navigator integration** - Enterprise metadata features
3. **Advanced sample navigation** - UX improvements
4. **Query/Browse individual partitions** - Enhanced partition management

---

## Tab Visibility Reference (Legacy Metastore Conditions)

### Always Visible Tabs
- **Overview** - Always shown for all tables
- **Schema** - Always shown for all tables  
- **Sample** - Always shown for all tables
- **Details** - Always shown for all tables

### Conditionally Visible Tabs
- **Partitions** - Only when `tableDetails().partition_keys.length > 0`
- **View SQL** - Only when `catalogEntry.isView() === true` (database views only)
- **ERD/Relationships** - Only when `SHOW_TABLE_ERD` config is `True` (disabled by default)
- **Privileges** - Only when `has_navigator_enabled() === true` (Navigator integration)

### Non-Existent Tabs
- **Queries** - This was never a real tab, just content within other areas when SQL Analyzer enabled

---

*This analysis identifies specific gaps between the legacy Metastore and React Table Browser implementations, focusing only on UI features that were actually exposed to users in the original interface. Use this to prioritize development efforts for achieving full feature parity.*
