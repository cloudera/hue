## Table Browser React Testing TODO

This document tracks per-file test coverage and progress for `desktop/core/src/desktop/js/apps/tableBrowserReact`.

Legend: [ ] = needs work, [x] = sufficiently covered

Summary (current): 54.62% statements, 42.84% branches, 51.23% functions, 54.38% lines

### Files

- [ ] TableBrowserPage.tsx — lines 24.88%, branches 20.58%
- [ ] index.ts — lines 0%
- [x] ColumnDetails/ColumnDetails.tsx — lines 79.24%
- [ ] DatabaseListing/DatabaseProperties.tsx — lines 8.33%
- [x] DatabaseListing/DatabasesList.tsx — lines 67.64%
- [ ] SourceListing/SourcesList.tsx — lines 4%
- [ ] TableDetails/TableDetails.tsx — lines 0%
- [ ] TableDetails/DetailsTab/DetailsProperties.tsx — lines 0%
- [x] TableDetails/ImportDataModal/ImportDataModal.tsx — lines 94.54%
- [x] TableDetails/OverviewTab/Overview.tsx — lines 87.5%
- [ ] TableDetails/OverviewTab/Schema.tsx — lines 50.81%
- [x] TableDetails/PartitionsTab/Partitions.tsx — lines 59.28%
- [ ] TableDetails/PrivilegesTab/Privileges.tsx — lines 0%
- [ ] TableDetails/QueriesTab/Queries.tsx — lines 0%
- [ ] TableDetails/SampleTab/SampleGrid.tsx — lines 3.22%
- [x] TableDetails/ViewSqlTab/ViewSql.tsx — lines 65.11%
- [x] TableListing/TablesList.tsx — lines 70.19%
- [x] TypeDetails/TypeDetails.tsx — lines 81.11%
- [ ] hooks/useTableBrowserController.ts — lines 0%
- [ ] hooks/useTableDetails.ts — lines 18.9%
- [x] hooks/useDatabaseProperties.ts — lines 91.3%
- [x] hooks/useDescriptionManager.ts — lines 100%
- [x] sharedComponents/Breadcrumbs.tsx — lines 91.3%
- [ ] sharedComponents/InlineDescriptionEditor.tsx — lines 7.14%
- [ ] sharedComponents/MetaDataDisplay.tsx — lines 25%
- [x] sharedComponents/NavigationContext.tsx — lines 100%
- [x] sharedComponents/PageHeader.tsx — lines 100%
- [x] sharedComponents/PrettyStructDisplay.tsx — lines 84.01%
- [x] sharedComponents/TableBrowserErrorBoundary.tsx — lines 100%
- [x] sharedComponents/Tabs.tsx — lines 100%
- [x] sharedComponents/Toolbar.tsx — lines 100%
- [ ] utils/connector.ts — lines 0%
- [ ] utils/notifier.ts — lines 50%
- [x] utils/routing.ts — lines 86.66%

### Next Targets

1) Raise `useTableDetails.ts` to ≥50% lines by covering:
- analysis.details.stats normalization (size/time formatting)
- view vs table sample gating via hue config
- partition count fetch path (partitioned vs non)

2) Cover tabs currently at 0–5%:
- DetailsTab/DetailsProperties.tsx: search + pagination; linkifying Location
- PrivilegesTab/Privileges.tsx: loading, empty, error, populated
- QueriesTab/Queries.tsx: various input missing states, successful list, empty
- SampleTab/SampleGrid.tsx: header trimming, pagination reset on page size change, empty state

3) Medium improvements:
- OverviewTab/Schema.tsx: more facet combinations, count callback
- InlineDescriptionEditor.tsx and MetaDataDisplay.tsx minimal smoke tests

### Deltas To Track

After each improvement, re-run coverage scoped to tableBrowserReact and update this file by checking off items and adjusting percentages.
