# Table Browser React - Refactor & Quality Plan

This TODO tracks the planned fixes and improvements from the recent review. We will proceed tests-first to prevent regressions.

## 1) Tests-first hardening (expand coverage)
- [x] Add tests for ErrorBoundary fallback UI and retry/refresh actions (already existed)
- [x] Add tests for struct navigation:
  - [x] TypeDetails: drilling into nested fields; flattened toggle; sample values shown
  - [x] ColumnDetails: flattened vs top-level view and nested navigation (already existed)
- [x] Add tests for DatabasesList:
  - [x] Create Database modal validation & submission
  - [x] Drop confirmation flows (single/multiple), skip-trash toggle
- [x] Add tests for TablesList:
  - [x] Toolbar actions (New/View/Query/Drop) enabled states and behaviors
  - [ ] Description editing flows
- [x] Add routing tests for Breadcrumbs clicks and deep field navigation
- [x] Add tests for Tabs to ensure no focus loss when counts change
- [x] Add ViewSql extraction test for multiple-line SQL stitching

## 2) Fix Error Boundary
- [x] Convert to functional boundary using `react-error-boundary` with i18n fallback
- [x] Ensure i18n usage is valid and accessible labels are present
- [x] Add/verify unit tests (retry + refresh)

## 3) Styling: remove inline styles and hardcoded colors
- [x] InlineDescriptionEditor: moved to SCSS, BEM classes
- [x] Breadcrumbs: extract inline styles to SCSS, use tokens
- [x] DatabasesList: extract inline styles, use tokens
- [x] TablesList: extract inline styles, use tokens
- [x] Schema/ColumnDetails/DetailsProperties: extract inline styles, use tokens
- [ ] Replace magic pixel values with spacing tokens (where safe)
-   - Progress: updated `ColumnDetails.scss` (margins/gaps to tokens; min-height converted to rem)
    - Progress: updated `Schema.scss` (gap, popover widths to rem/tokens)
    - Progress: updated `TypeDetails.scss` (gap to token)
    - Progress: updated `Privileges.scss` (padding/gaps/margins to tokens)
    - Progress: updated `TableBrowserPage.scss` (layout spacing to tokens/rem)
    - Progress: updated `PrettyStructDisplay.scss` (font sizes to rem)
    - Progress: updated `ImportDataModal.scss` (margins/labels/notes to tokens)
- [x] Ensure `.cuix.antd` root and BEM names

## 4) i18n pass
- Localize remaining literals (e.g., UNKNOWN, aria labels, default strings in PrettyStructDisplay)
  - [x] Localize 'UNKNOWN' in `useTableDetails`
  - [x] Localize PrettyStructDisplay default aria label
- Audit placeholders, button titles, error messages for i18n

## 5) Tabs stability and focus preservation
- [x] Restore key stabilization and ink animation suppression workaround
- [x] Ensure keyboard focus remains on the active tab when labels/counts change
- [x] Tests cover focus and label updates

## 6) Navigation context
- [x] Introduce `NavigationProvider` to provide route, basePath, and navigation callbacks
- [x] Update PageHeader/Breadcrumbs/TableDetails consumers to use context rather than prop drilling

## 7) Description editing reuse
- [ ] Extract table/db/column description editing patterns into a reusable component
- [x] Adopt in TablesList
- [x] Adopt in DatabasesList and Schema
- [ ] Consolidate behaviors (save, cancel, skeleton) and tests

## 8) Breadcrumbs refactor
- [x] Use `utils/routing` helpers for base path and path building
- [x] Extract inline styles to SCSS and ensure link semantics/aria are correct

## 9) Cleanup & utilities
- Remove debug logs and stray console statements
- Standardize timestamps via `formatTimestamp`

## 10) Headers & lint
- Ensure all files have Cloudera license header (e.g., PrettyStructDisplay.tsx)
- Run lints and fix style/import order as needed
  - [x] Added license header to `sharedComponents/PrettyStructDisplay.tsx`

## 11) Introduce state hooks
- Extract the logic for each "sub page" into its own custom hook for cleaner state management
  - [x] Extracted `useImportDataForm` and integrated into `TableDetails/ImportDataModal/ImportDataModal.tsx`
  - [x] Extracted `useTablesListState` and integrated into `TableListing/TablesList.tsx`
  - [x] Extracted `useTableDetailsState` and integrated into `TableDetails/TableDetails.tsx` (drop confirm, skipTrash, import modal)
  - [x] Lifted UI state to `TableBrowserPage` and passed `ui` down to `TableDetails` and `TablesList`
  - [x] DatabasesList: consolidated to single `useDatabasesListState` (includes filter/pagination + description editing + isInitializing); `TableBrowserPage` passes one `state` object
    - [x] Generalized `ListCellEditState` interface for reusable cell editing patterns
  - [x] SourcesList: consolidated to single `useSourcesListState` (includes filter/pagination + isInitializing); `TableBrowserPage` passes one `state` object
  - [x] TablesList: consolidated to single `useTablesListState` (includes filter/pagination + UI state + description editing + isInitializing); `TableBrowserPage` passes one `state` object
  - [x] TableDetails: consolidated to single `useTableDetailsState` (includes tab state + table data fetching + UI state); `TableBrowserPage` passes one `state` object
  - [ ] Add focused hook for TableDetails tab state (coordinate with `useTableBrowserController`)
  - [ ] Identify remaining local component states to consolidate where it reduces prop drilling

## 12) Review function and variable naming throughout the TableBrowserpage and subcomponents.
- [x] Understand and fix example with name "editingTableName" that is in reality a flag for editing a table column, not table name.
- Search for and improve other inconsistent namings
 
<!-- ## 13) Quick wins
- [ ] Extract metastore actions into `utils/metastoreActions.ts`
  - [ ] `dropDatabases({ names, connector, namespace, compute, sourceType })`
  - [ ] `dropTables({ database, names, skipTrash, connector, namespace, compute, sourceType })`
  - [ ] `createDatabase({ name, comment?, location?, connector?, namespace?, compute?, sourceType? })`
- [ ] Add connector utilities in `utils/connectorUtils.ts`
  - [ ] `findConnectorByTypeOrId(connectors, src)`
  - [ ] `uniqueSourceTypes(connectors)`
- [ ] Add filter utilities in `utils/filterUtils.ts`
  - [ ] `getSearchString(FilterOutput)`
- [ ] Use `NavigationContext` in `Breadcrumbs`/`PageHeader`/list components to drop redundant onClick props
- [ ] Introduce shared `ConfirmModal` in `sharedComponents` for database/table drop confirmations -->
