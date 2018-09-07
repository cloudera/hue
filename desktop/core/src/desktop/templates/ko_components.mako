## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%namespace name="koAppSwitcher" file="/ko_components/ko_app_switcher.mako" />
<%namespace name="koBreadCrumbs" file="/ko_components/ko_breadcrumbs.mako" />
<%namespace name="koCatalogEntriesTable" file="/ko_components/ko_catalog_entries_table.mako" />
<%namespace name="koContextPopover" file="/ko_components/ko_context_popover.mako" />
<%namespace name="koContextSelector" file="/ko_components/ko_context_selector.mako" />
<%namespace name="koDropDown" file="/ko_components/ko_drop_down.mako" />
<%namespace name="koFavoriteApp" file="/ko_components/ko_favorite_app.mako" />
<%namespace name="koGlobalSearch" file="/ko_components/ko_global_search.mako" />
<%namespace name="koHistoryPanel" file="/ko_components/ko_history_panel.mako" />
<%namespace name="koInlineAutocomplete" file="/ko_components/ko_inline_autocomplete.mako" />
<%namespace name="koJobBrowserLinks" file="/ko_components/ko_job_browser_links.mako" />
<%namespace name="koMultiClusterSidebar" file="/ko_components/ko_multi_cluster_sidebar.mako" />
<%namespace name="koNavProperties" file="/ko_components/ko_nav_properties.mako" />
<%namespace name="koNavTags" file="/ko_components/ko_nav_tags.mako" />
<%namespace name="koSimpleAceEditor" file="/ko_components/ko_simple_ace_editor.mako" />
<%namespace name="koSqlColumnsTable" file="/ko_components/ko_sql_columns_table.mako" />
<%namespace name="koDeleteDocModal" file="/ko_components/ko_delete_doc_modal.mako" />
<%namespace name="koSentryPrivileges" file="/ko_components/ko_sentry_privileges.mako" />
<%namespace name="koCreateDirModal" file="/ko_components/ko_create_directory_modal.mako" />

<%def name="all()">
  ${ koAppSwitcher.appSwitcher() }
  ${ koBreadCrumbs.breadCrumbs() }
  ${ koCatalogEntriesTable.catalogEntriesTable() }
  ${ koContextPopover.contextPopover() }
  ${ koContextSelector.contextSelector() }
  ${ koDropDown.dropDown() }
  ${ koFavoriteApp.favoriteApp() }
  ${ koGlobalSearch.globalSearch() }
  ${ koHistoryPanel.historyPanel() }
  ${ koInlineAutocomplete.inlineAutocomplete() }
  ${ koJobBrowserLinks.jobBrowserLinks() }
  ${ koMultiClusterSidebar.multiClusterSidebar() }
  ${ koNavProperties.navProperties() }
  ${ koNavTags.navTags() }
  ${ koSimpleAceEditor.simpleAceEditor() }
  ${ koSqlColumnsTable.sqlColumnsTable() }
  ${ koDeleteDocModal.deleteDoc() }
  ${ koSentryPrivileges.sentryPrivileges() }
  ${ koCreateDirModal.createDirectory() }
</%def>