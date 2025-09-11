## Table Browser React Migration TODO (Steps 1–7)

- [x] 1) Backend: feature flag and config plumbing
  - [x] Add `ENABLE_NEW_TABLE_BROWSER` in `desktop/core/src/desktop/conf.py`
    - [x] `key="enable_new_table_browser"`, type `coerce_bool`, default `False`, help text.
  - [x] Expose to frontend globals in `desktop/core/src/desktop/templates/global_js_constants.mako`
    - [x] `window.ENABLE_NEW_TABLE_BROWSER = '${ hasattr(ENABLE_NEW_TABLE_BROWSER, 'get') and ENABLE_NEW_TABLE_BROWSER.get() }' === 'True';`
  - [x] Expose in config API `desktop/core/src/desktop/api2.py#get_config`
    - [x] Add `config['table_browser'] = { 'enable_new_table_browser': ENABLE_NEW_TABLE_BROWSER.get() }`.
  - [x] Add commented sample to `desktop/conf/pseudo-distributed.ini.tmpl` for easy enabling.

- [x] 2) Backend: navigation target URL
  - [x] Update the `ClusterConfig` builder in `desktop/core/src/desktop/models.py` where `app_config.browser.interpreters` is assembled.
    - [x] For interpreter with `type == 'tables'`:
      - [x] If `ENABLE_NEW_TABLE_BROWSER.get()`: set `page` to `/tablebrowser/`.
      - [x] Else keep existing Metastore URL.
  - [x] Verify the sidebar link updates automatically since `HueSidebar.vue` consumes `app_config`.

- [x] 3) Frontend SPA: new route and React root
  - [x] Create a new React app directory: `desktop/core/src/desktop/js/apps/tableBrowserReact/` with:
    - [x] `TableBrowserPage.tsx` (entry)
    - [ ] Optional subcomponents: `DatabaseListPane`, `TableListPane`, `TableDetails`
    - [x] `TableBrowserPage.scss` using BEM (`.hue-table-browser`)
  - [x] Wire SPA route in `desktop/core/src/desktop/js/onePageViewModel.js`:
    - [x] `import TableBrowserPage from '../js/apps/tableBrowserReact/TableBrowserPage';`
    - [x] Add to `pageMapping`:
      - [x] `url: '/tablebrowser/'`
      - [x] `app: () => showReactAppPage({ appName: 'tablebrowser', component: TableBrowserPage, title: 'Table Browser' })`
    - [ ] Optionally gate route registration with `if (window.ENABLE_NEW_TABLE_BROWSER) { ... }`.
  - [x] Confirm `showReactAppPage()` creates the React root under `.page-content` (no template changes needed).
  - [x] Add minimal URL sync logic (db/table) for verification

- [x] 4) URL model and redirects
  - [x] Support URLs:
    - [x] `/tablebrowser/<sourceType>`
    - [x] `/tablebrowser/<sourceType>/<database>`
    - [x] `/tablebrowser/<sourceType>/<database>/<table>`
    - [ ] Optional: `?connector_id=<id>`
  - [x] In React, read URL params/search and keep them in sync using `changeURL` when selection changes.
  - [x] Optional client-side redirects in `onePageViewModel.js` (only when flag is enabled):
    - [x] Redirect key legacy Metastore paths (e.g., describe/browse) to the new `/tablebrowser/...` equivalents.
    - [ ] If needed for direct hits, add guarded Django redirects in `apps/metastore/src/metastore/urls.py`.

- [ ] 5) Data/APIs
  - [x] Reuse existing Metastore endpoints in `apps/metastore/src/metastore/urls.py` for:
    - [x] Databases list
    - [x] Tables list
    - [x] Table metadata/details
    - [x] Partitions
    - [x] Samples (read)
    - [ ] Queries
  - [x] Fetch via Data Catalog hook (`useDataCatalog`) for databases/tables.
  - [ ] Use `useLoadData` for table details and provide retry.

- [x] 6) Sidebar and deep-link behavior
  - [x] With step 2 in place, the sidebar (`desktop/core/src/desktop/js/components/sidebar/HueSidebar.vue`) should point the Tables item to `/tablebrowser/` under the flag.
  - [x] For the new `tablebrowser` item, deep-link with `/tablebrowser/:sourceType/:database` using current Assist/Editor selection.

- [x] 7) i18n, styling, accessibility
  - [x] All user-facing strings via `i18nReact`.
  - [x] Styling with SCSS+BEM in `TableBrowserPage.scss`; block `.hue-table-browser` and `__element` modifiers.
  - [x] Use `cuix` and `antd` components; avoid CSS Modules and hardcoded colors.
  - [ ] Ensure keyboard navigation, roles/labels for lists, tabs, and data tables.

## UI spec to match legacy Table view (expanded TODO)

- [ ] Global page layout
  - [x] Breadcrumbs: `<sourceType> > Databases > <database> > <table>` with links back to `Databases` and the selected `<database>` (navigates in-app).
  - [x] Datasource dropdown in breadcrumbs updates connector + URL immediately.
  - [x] Header title: `<database> > <table>` with icon.
  - [x] Toolbar actions (right-aligned):
    - [x] Query: opens Editor with snippet type = `<sourceType>`.
    - [x] Drop: confirm modal; on success, navigate to `/tablebrowser/:sourceType/:database`.
    - [x] Refresh: invalidates catalog entry and reloads table metadata.
  - [x] Loading and error banners using `GlobalAlert` topics where applicable.

- [ ] Left navigation pane
  - [x] List databases (from Data Catalog) and keep URL in sync.
  - [x] List tables for selected DB and keep URL in sync.
  - [x] Add search filter for databases and tables.
  - [x] Show description column for DBs and tables with inline edit.
  - [x] Show skeleton on load and consistent empty states.
  - [ ] Virtualize long lists. (skipped for now)

- [ ] Right content: Tabs and content
  - [x] Tabs: `Overview`, `Partitions`, `Sample (N)`, `Queries`, `View SQL`, `Details`, `Privileges`.
  - [x] Tab state in URL: `?tab=overview|partitions|sample|queries|viewSql|details|privileges` (default `overview`).

  - [ ] Overview tab
    - [ ] Properties panel:
      - [x] Show storage location (link opens File Browser), table managed/external, owner/created time.
      - [ ] Show other key-value pairs surfaced by metastore (`parameters`, `serde`, etc.) when available.
    - [x] Stats panel:
      - [x] Files, Rows, Total size; small Refresh icon to recompute table stats.
      - [x] “Last updated” timestamp.
    - [ ] Actions area mirrors toolbar (optional secondary access).

  - [ ] Partitions tab (parity with legacy Metastore)
    - [ ] Partition columns panel
      - [ ] Table with index, column name, and type for partition keys.
    - [x] Partitions list panel
      - [x] Columns: Values (clickable to query), Spec, Browse (hidden for Impala).
      - [x] Values cell action: open Editor with partition query (compose `SELECT * FROM <db>.<table> WHERE <spec>`).
      - [x] Browse action: open Storage Browser to the partition folder (`browseUrl`).
      - [x] Loading spinner while fetching; empty state when no values.
    - [ ] Filtering UX (multi-filter like legacy)
      - [x] Add/remove filter rows; each row selects a partition key and a value.
      - [x] Typeahead suggestions for values based on existing partition values for the selected key.
      - [ ] Sort Desc toggle; Filter button to apply; “Add a filter” affordance when none present. (Sort + add implemented; explicit Apply button pending)
      - [ ] Persist filters and sort in component state and re-fetch when applied. (Client-side filtering in place; server-side refetch TBD)
    - [x] Selection and bulk actions
      - [x] Row selection with check-all and per-row checkboxes.
      - [x] Drop partition(s) button (write-access only) with confirmation modal.
      - [x] Call existing endpoint: `POST /metastore/table/<db>/<table>/partitions/drop` with selected specs.
    - [ ] Counts and navigation
      - [ ] Show partitions count badge in tab label. (Component support added; wiring from page pending)
      - [x] Pagination/virtualization for large lists (TBD; basic pagination acceptable initially).
    - [ ] Permissions and source-specific behavior
      - [x] Hide Browse column for Impala sources (match legacy behavior).
      - [ ] Gate destructive actions by write access. (Server enforces; UI gating optional/pending)
    - [x] Accessibility and i18n
      - [x] Keyboard navigable filters, list, and actions; all strings via `i18nReact`.
    - [x] Data wiring
      - [x] Use Data Catalog `getPartitions()` result: `partition_keys_json`, `partition_values_json[{ columns, partitionSpec, browseUrl, notebookUrl, readUrl }]`.
      - [x] Implement value typeahead from current partitions set; consider backend support if needed later.

  - [x] Sample tab
    - [x] Fetch sample rows via Data Catalog.
    - [x] Data grid with horizontal scroll; pagination TBD.
    - [x] Loading state.

  - [x] Queries tab (basic)
    - [x] List popular join predicates as placeholder; replace with `/metastore/table/<db>/<table>/queries`.
    - [x] Empty state: “No queries found for the current table.”

  - [x] View SQL tab (for views)
    - [x] Renders view SQL when available.

  - [x] Details tab
    - [x] Schema grid with columns: `Column`, `Type`, `Description`.
    - [x] Filter input above the grid to search columns by name/description.
    - [ ] Render info icon next to column names when extra metadata exists.
    - [ ] Hook data for column samples if available.

  - [x] Privileges tab
    - [x] Placeholder; integrate KO `hue-sentry-privileges` via `reactWrapper` later.

- [ ] Routing and URL model
  - [x] Base paths: `/tablebrowser/:sourceType/:database[/::table]` without trailing slash.
  - [x] Add `?tab=` query param; updating tab should push history via `changeURL`.
  - [ ] Maintain deep-link behavior from the sidebar (db pre-selected) and legacy redirects.

- [ ] Data fetching and caching
  - [x] Databases and Tables via `useDataCatalog` for `<sourceType>` connector.
  - [x] Table analysis/details via Data Catalog (`getAnalysis`).
  - [x] Sample rows via Data Catalog (`getSample`).
  - [x] Partitions list via Data Catalog (`getPartitions`).
  - [ ] Add retries and error banners with `LoadingErrorWrapper`.
  - [x] Invalidate-and-refresh hooks when clicking Refresh (and after Drop).

- [ ] Toolbar actions: implementations
  - [x] Query: publish `open.editor.new.query` with type=`<sourceType>` and prefill `FROM <db>.<table>`.
  - [x] Drop: call existing metastore drop endpoint; confirm modal, success toast, redirect back to DB.
  - [x] Refresh: trigger stats/metadata refresh; refetch details and sample.
  - [x] Optional: `Load Data` if enabled (call `/metastore/table/<db>/<table>/load`).

- [ ] UX polish
  - [x] Show counts (e.g., `Sample (100)`) once data is loaded; otherwise show `Sample`.
  - [x] Preserve selection and tab on reload via URL; default to Overview.
  - [ ] Keyboard focus management when switching tabs and filtering schema grid.
  - [ ] Consistent empty states across tabs.
  - [ ] Link out to Optimizer and Navigator URLs if configured.


## Follow-up TODOs from PR Review

- [x] Simplify view derivation from URL
  - [x] Remove `forceShowSources` local flag; derive view strictly from route (no sourceType => sources view)
  - [x] Drop `?view=sources` idea and ensure sources view is only at `/tablebrowser/`

- [x] Split `TableBrowserPage.tsx` into cohesive subcomponents
  - [x] Create `SourcesList` (filter, pagination, selection)
  - [x] Create `DatabasesList` (filter, pagination, inline description edit)
  - [x] Create `TablesList` (filter, pagination, inline description edit)
  - [x] Wire subcomponents into `TableBrowserPage.tsx` (replace inline blocks)

- [x] Improve refresh spinner lifecycle
  - [x] Tie spinner to async operations (clearCache + subsequent list fetch) instead of `setTimeout`
  - [ ] Optionally enforce a short min-display time to avoid flicker

- [x] Harden error handling across lists
  - [x] Ensure sources/DBs/tables lists guard undefined inputs and connector failures
  - [x] Render consistent `EmptyState` on errors and publish a `GlobalAlert` with a short message

- [x] Accessibility and focus management
  - [x] Move focus to main panel container after crumb navigation (sources/DBs/tables)
  - [x] Verify breadcrumbs use `aria-current` appropriately for active crumb

- [x] Naming and cleanup
  - [x] Remove commented/unreferenced props/imports in `Breadcrumbs.tsx`
  - [x] Extract URL build/parsing helpers to a small routing util (`utils/routing.ts`)


## BUGS FOUND DURING TESTING
- [ ] Tooltips in toolbar not showing


## Architecture & Refactoring Plan (Phase 2)

### Goals
- Improve cohesion, testability, and type safety of the Table Browser React app.
- Centralize routing and data-fetching concerns; reduce duplication and unsafe casts.
- Ensure accessibility, i18n, and styling adhere to workspace golden rules.

### 1) State management and controllers
[x] Create `useTableBrowserController` hook that owns URL ⇄ selection synchronization and list state:
  [x] Responsibilities: parse/build path, current `sourceType`, `database`, `table`, `activeTab`, and navigation helpers.
  [ ] Manage filters and pagination for sources, databases, and tables.
  [ ] Manage inline description editing state and save actions with optimistic updates.
  [x] Expose a minimal, typed API for the page and list components to consume.
[ ] Outcome: `TableBrowserPage.tsx` focuses on layout/composition; list components remain presentational.

### 2) Data fetching hooks
[x] Create `useTableDetails` for analysis, stats, details sections, schema columns, and sample data.
  [x] API: `{ loading, overviewProps, detailsSections, detailsProperties, columns, sampleData, refresh }`.
[ ] Create `usePartitionsData` encapsulating partitions list, filters, sorting, and actions (drop, open editor, browse folder).
[ ] Benefits: coalesce catalog calls, simplify effects, and isolate error handling.

### 3) Routing utilities
[x] Add `getTableBrowserBasePath(pathname?: string): string` that returns the base path before `/tablebrowser`.
[x] Keep `parseTableBrowserPath()` and `buildTableBrowserPath()` as single sources of truth; use them everywhere.
[x] Ensure query param handling for `?tab=` is consistent; avoid scattering `changeURL` logic across components.

### 4) Types and safety
[ ] Define typed interfaces for:
  [ ] Connector summary `{ id?: string; type: string; ... }`.
  [ ] Analysis payload (details/stats/cols) with narrow optional fields.
  [ ] Table overview models (`TableStats`, `OverviewProperty`, etc.).
  [ ] Partitions payload (`partition_keys_json`, `partition_values_json`).
[ ] Replace `unknown`/`any` casts with typed helpers and narrowings.

### 5) Component cohesion & splits
[ ] Keep `SourcesList`, `DatabasesList`, `TablesList` as presentational with typed props.
[ ] Move navigation actions and base path handling into the controller; pass callbacks only.
[ ] Extract small presentational pieces (e.g., description editor) if needed for reuse and clarity.

### 6) Error handling & notifications
[ ] Introduce a tiny notifier utility to publish `GLOBAL_ERROR_TOPIC`/`GLOBAL_INFO_TOPIC` with consistent messages.
[ ] Replace silent `catch {}` with explicit, silenced notifications or dev logging.
[ ] Show consistent `EmptyState` on errors where lists/details cannot load.

### 7) Accessibility & i18n
[ ] Ensure all icon-only buttons have an accessible name (`aria-label`).
[x] Avoid JS-based text transforms (e.g., `.toUpperCase()`); use CSS instead.
[x] i18n all labels including the `ERD` tab.
[ ] Maintain focus management after navigation (already added for main panel); extend to tabs if needed.

### 8) Styling cleanup
[ ] Remove hardcoded colors and inline styles; use SCSS tokens/variables and BEM classes.
[ ] Fix `font` shorthand usage; prefer `font-family` and tokenized font variables.
[ ] Keep overrides for Ant components minimal and scoped under `.hue-table-browser`.

### 9) Tests
[x] Add missing license headers to test files.
[ ] Prefer `userEvent` over `fireEvent` in navigation tests.
[ ] Add tests for:
  [ ] Description edit/save/cancel for DBs and tables (success/error flows).
  [ ] Refresh actions (databases/tables), ensuring loading states and cache clear are invoked.
  [ ] Partitions filters/sorting and drop confirmation behavior.
  [ ] Tabs: URL `?tab=` sync.

### 10) Performance & UX polish
[ ] Reset pagination on filter changes; preserve through URL if needed later.


### Implementation Steps (sequenced)
1. Routing utils: add `getTableBrowserBasePath()`; refactor `TableBrowserPage.tsx` to use it.
2. Tighten `useEffect` dependencies and centralize error notifications in the page.
3. Introduce `useTableBrowserController` and wire list panes to it; remove inline base/URL logic from handlers.
4. Extract `useTableDetails`; move analysis/sample building logic out of the page.
5. Type cleanup: add interfaces and replace unsafe casts across the app.
6. A11y/i18n fixes (Tabs ERD, icon buttons, uppercase via CSS).
7. Styling cleanup (SCSS tokens, remove inline styles, fix font usage).
8. Tests: headers, userEvent migration, new coverage for edits/refresh/partitions.
