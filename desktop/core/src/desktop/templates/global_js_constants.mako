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

<%!
  from django.utils.translation import ugettext as _

  from desktop import conf
  from desktop.auth.backend import is_admin, is_hue_admin
  from desktop.conf import APP_SWITCHER_ALTUS_BASE_URL, APP_SWITCHER_MOW_BASE_URL, CUSTOM_DASHBOARD_URL, \
      DISPLAY_APP_SWITCHER, IS_K8S_ONLY, IS_MULTICLUSTER_ONLY, USE_DEFAULT_CONFIGURATION, USE_NEW_SIDE_PANELS, \
      VCS, ENABLE_GIST, ENABLE_LINK_SHARING, has_channels, has_connectors
  from desktop.models import hue_version, _get_apps, get_cluster_config

  from beeswax.conf import DOWNLOAD_BYTES_LIMIT, DOWNLOAD_ROW_LIMIT, LIST_PARTITIONS_LIMIT, CLOSE_SESSIONS
  from dashboard.conf import HAS_SQL_ENABLED
  from jobbrowser.conf import ENABLE_HISTORY_V2
  from filebrowser.conf import SHOW_UPLOAD_BUTTON, REMOTE_STORAGE_HOME
  from indexer.conf import ENABLE_NEW_INDEXER
  from metadata.conf import has_catalog, has_readonly_catalog, has_optimizer, has_workload_analytics, OPTIMIZER, get_optimizer_url, \
      get_catalog_url, get_optimizer_mode
  from metastore.conf import ENABLE_NEW_CREATE_TABLE
  from metastore.views import has_write_access
  from notebook.conf import ENABLE_NOTEBOOK_2, ENABLE_QUERY_ANALYSIS, ENABLE_QUERY_BUILDER, ENABLE_QUERY_SCHEDULING, ENABLE_SQL_INDEXER, \
      get_ordered_interpreters, SHOW_NOTEBOOKS
%>

<%namespace name="sqlDocIndex" file="/sql_doc_index.mako" />
(function () {
  <%
    apps = _get_apps(user)[2]
  %>

  window.AUTOCOMPLETE_TIMEOUT = ${ conf.EDITOR_AUTOCOMPLETE_TIMEOUT.get() };

  window.BANNER_TOP_HTML = '${ conf.CUSTOM.BANNER_TOP_HTML.get() }';

  window.DISABLE_LOCAL_STORAGE = '${ conf.DISABLE_LOCAL_STORAGE.get() }' === 'True';

  window.CACHEABLE_TTL = {
    default: ${ conf.CUSTOM.CACHEABLE_TTL.get() },
    optimizer: ${ OPTIMIZER.CACHEABLE_TTL.get() or 0 }
  };

  window.DEV = '${ conf.DEV.get() }' === 'True';

  %if request and request.COOKIES and request.COOKIES.get('csrftoken', '') != '':
    window.CSRF_TOKEN = '${request.COOKIES.get('csrftoken')}';
  %else:
    window.CSRF_TOKEN = '';
  %endif

  window.PREVENT_AUTOFILL_INPUT_ATTRS = 'autocorrect="off" autocomplete="do-not-autocomplete" autocapitalize="off" spellcheck="false"';

  window.APP_SWITCHER_ALTUS_BASE_URL = '${ APP_SWITCHER_ALTUS_BASE_URL.get() }';
  window.APP_SWITCHER_MOW_BASE_URL = '${ APP_SWITCHER_MOW_BASE_URL.get() }';
  window.DISPLAY_APP_SWITCHER = '${ DISPLAY_APP_SWITCHER.get() }' === 'True';
  window.CUSTOM_LOGO = '${ conf.CUSTOM.LOGO_SVG.get() }' !== '';

  window.HAS_JOB_BROWSER = '${ 'jobbrowser' in apps }' === 'True';
  window.KNOX_BASE_PATH_HUE = '/KNOX_BASE_PATH_HUE';
  window._KNOX_BASE_PATH = '/KNOX_BASE_PATH_KNOX';
  window._KNOX_BASE_URL = '/KNOX_BASE_URL';
  window.HUE_BASE_URL = window.KNOX_BASE_PATH_HUE.indexOf('KNOX_BASE_PATH_HUE') < 0 ? window.KNOX_BASE_PATH_HUE : '';
  window.KNOX_BASE_PATH = window._KNOX_BASE_PATH.indexOf('KNOX_BASE_PATH_KNOX') < 0 ? window._KNOX_BASE_PATH_KNOX : '';
  window.KNOX_BASE_URL = window._KNOX_BASE_URL.indexOf('KNOX_BASE_URL') < 0 ? window._KNOX_BASE_URL : '';

  window.HAS_GIT = ${ len(VCS.keys()) } > 0;
  window.HAS_MULTI_CLUSTER = '${ get_cluster_config(user)['has_computes'] }' === 'True';

  window.HAS_SQL_DASHBOARD = '${ HAS_SQL_ENABLED.get() }' === 'True';
  window.CUSTOM_DASHBOARD_URL = '${ CUSTOM_DASHBOARD_URL.get() }';

  window.DROPZONE_HOME_DIR = '${ user.get_home_directory() if not user.is_anonymous else "" }';

  window.DOWNLOAD_ROW_LIMIT = ${ DOWNLOAD_ROW_LIMIT.get() if hasattr(DOWNLOAD_ROW_LIMIT, 'get') and DOWNLOAD_ROW_LIMIT.get() >= 0 else 'undefined' };
  window.DOWNLOAD_BYTES_LIMIT = ${ DOWNLOAD_BYTES_LIMIT.get() if hasattr(DOWNLOAD_BYTES_LIMIT, 'get') and DOWNLOAD_BYTES_LIMIT.get() >= 0 else 'undefined' };

  window.USE_DEFAULT_CONFIGURATION = '${ USE_DEFAULT_CONFIGURATION.get() }' === 'True';

  window.USER_HAS_METADATA_WRITE_PERM = '${ user.has_hue_permission(action="write", app="metadata") }' === 'True';

  window.ENABLE_DOWNLOAD = '${ conf.ENABLE_DOWNLOAD.get() }' === 'True';
  window.ENABLE_NEW_CREATE_TABLE = '${ hasattr(ENABLE_NEW_CREATE_TABLE, 'get') and ENABLE_NEW_CREATE_TABLE.get()}' === 'True';
  window.ENABLE_NOTEBOOK_2 = '${ ENABLE_NOTEBOOK_2.get() }' === 'True';
  window.ENABLE_PREDICT = '${ OPTIMIZER.ENABLE_PREDICT.get() }' === 'True';
  window.ENABLE_SQL_INDEXER = '${ ENABLE_SQL_INDEXER.get() }' === 'True';

  window.ENABLE_QUERY_BUILDER = '${ ENABLE_QUERY_BUILDER.get() }' === 'True';
  window.ENABLE_QUERY_SCHEDULING = '${ ENABLE_QUERY_SCHEDULING.get() }' === 'True';

  window.ENABLE_HISTORY_V2 = '${ hasattr(ENABLE_HISTORY_V2, 'get') and ENABLE_HISTORY_V2.get() }' === 'True';

  window.ENABLE_SQL_SYNTAX_CHECK = '${ conf.ENABLE_SQL_SYNTAX_CHECK.get() }' === 'True';

  window.HAS_CATALOG = '${ has_catalog(request.user) }' === 'True';
  window.CATALOG_URL = '${ get_catalog_url() or "" }'
  window.HAS_READ_ONLY_CATALOG = '${ has_readonly_catalog(request.user) }' === 'True' || '${ has_write_access(request.user) }' === 'False';

  window.HAS_OPTIMIZER = '${ has_optimizer() }' === 'True';
  window.OPTIMIZER_MODE = '${ get_optimizer_mode() }';
  window.OPTIMIZER_URL = '${ get_optimizer_url() }'
  window.AUTO_UPLOAD_OPTIMIZER_STATS = '${ OPTIMIZER.AUTO_UPLOAD_STATS.get() }' === 'True';

  window.HAS_GIST = '${ ENABLE_GIST.get() }' === 'True';
  window.HAS_CONNECTORS = '${ has_connectors() }' === 'True';

  ## In the past was has_workload_analytics()
  window.HAS_WORKLOAD_ANALYTICS = '${ ENABLE_QUERY_ANALYSIS.get() }' === 'True';

  window.SHOW_NOTEBOOKS = '${ SHOW_NOTEBOOKS.get() }' === 'True'
  window.SHOW_UPLOAD_BUTTON = '${ hasattr(SHOW_UPLOAD_BUTTON, 'get') and SHOW_UPLOAD_BUTTON.get() }' === 'True'

  window.IS_MULTICLUSTER_ONLY = '${ IS_MULTICLUSTER_ONLY.get() }' === 'True';
  window.IS_K8S_ONLY = '${ IS_K8S_ONLY.get() }' === 'True';
  window.JB_HEADER_CHECK_INTERVAL_IN_MILLIS = 30000;
  window.JB_SINGLE_CHECK_INTERVAL_IN_MILLIS = 5000;
  window.JB_MULTI_CHECK_INTERVAL_IN_MILLIS = 20000;
  window.CLOSE_SESSIONS = {'hive': '${ CLOSE_SESSIONS.get() }' === 'True'};

  window.HUE_URLS = {
    IMPORTER_CREATE_TABLE: '${ 'indexer' in apps and url('indexer:importer_prefill', source_type = 'all', target_type = 'table')}',
    IMPORTER_CREATE_DATABASE: '${ 'indexer' in apps and url('indexer:importer_prefill', source_type = 'manual', target_type = 'database')}',
    NOTEBOOK_INDEX: '${url('notebook:index')}',
    % if 'pig' in apps:
    PIG_INDEX: '${url('pig:index')}',
    % endif
    % if 'oozie' in apps:
    OOZIE_NEW_WORKFLOW: '${url('oozie:new_workflow')}',
    OOZIE_NEW_COORDINATOR: '${url('oozie:new_coordinator')}',
    OOZIE_NEW_BUNDLE: '${url('oozie:new_bundle')}',
    % endif
    % if 'search' in apps:
    SEARCH_NEW_SEARCH: '${url('search:new_search')}',
    % endif
  }

  // TODO: Replace with json import
  window.HUE_I18n = {
    '1 hour':  '${ _('1 hour') }',
    '1 week':  '${ _('1 week') }',
    '8 hours':  '${ _('8 hours') }',
    'Active cluster': '${ _('Active cluster') }',
    'Active compute': '${ _('Active compute') }',
    'Active database': '${ _('Active database') }',
    'Active namespace': '${ _('Active namespace') }',
    'Add a description...': '${ _('Add a description...') }',
    'Add filter': '${ _('Add filter') }',
    'Add privilege': '${ _('Add privilege') }',
    'Add properties...': '${ _('Add properties...') }',
    'Add table': '${ _('Add table') }',
    'Add tags...': '${ _('Add tags...') }',
    'Add': '${ _('Add') }',
    'Admin': '${ _('Admin') }',
    'Administration': '${ _('Administration') }',
    'Administer Server': '${ _('Administer Server') }',
    'Administer Users': '${ _('Administer Users') }',
    'aggregate': '${ _('aggregate') }',
    'Aggregate': '${ _('Aggregate') }',
    'alias': '${ _('alias') }',
    'All': '${_('All')}',
    'An error occurred refreshing the table stats. Please try again.': '${_('An error occurred refreshing the table stats. Please try again.')}',
    'Analysis was not possible for the executed query.': '${_('Analysis was not possible for the executed query.')}',
    'and': '${_('and')}',
    'Apps': '${ _('Apps') }',
    'Are you sure you want to clear the task history?': '${ _('Are you sure you want to clear the task history?') }',
    'Assist': '${ _('Assist') }',
    'Assistant': '${ _('Assistant') }',
    'at cursor': '${ _('at cursor') }',
    'Australia': '${ _('Australia') }',
    'Back': '${_('Back')}',
    'Bar Chart': '${ _('Bar Chart') }',
    'Bars': '${ _('Bars') }',
    'Brazil': '${ _('Brazil') }',
    'Browse column privileges': '${_('Browse column privileges')}',
    'Browse db privileges': '${ _('Browse db privileges') }',
    'Browse DB privileges': '${_('Browse DB privileges')}',
    'Browse table privileges': '${_('Browse table privileges')}',
    'Browsers': '${ _('Browsers') }',
    'Bundle': '${ _('Bundle') }',
    'Canada': '${ _('Canada') }',
    'Cancel upload': '${ _('Cancel upload') }',
    'Cancel': '${_('Cancel')}',
    'Change': '${ _('Change') }',
    'Chart': '${ _('Chart') }',
    'Check compatibility': '${ _('Check compatibility') }',
    'China': '${ _('China') }',
    'Choose a column to pivot...': '${ _('Choose a column to pivot...') }',
    'Choose a column...': '${ _('Choose a column...') }',
    'Choose a scope...': '${ _('Choose a scope...') }',
    'Choose a type...': '${ _('Choose a type...') }',
    'Choose...': '${ _('Choose...') }',
    'Clear cache': '${ _('Clear cache') }',
    'Clear the current editor': '${ _('Clear the current editor') }',
    'Clear the query history': '${ _('Clear the query history') }',
    'Clear': '${ _('Clear') }',
    'Click for more details': '${ _('Click for more details') }',
    'Close session': '${_('Close session')}',
    'Close': '${_('Close')}',
    'Cluster': '${ _('Cluster') }',
    'Clusters': '${ _('Clusters') }',
    'CodeGen': '${ _('CodeGen') }',
    'Collapse': '${ _('Collapse') }',
    'Collection': '${ _('Collection') }',
    'column name...': '${_('column name...')}',
    'Column': '${ _('Column') }',
    'Columns': '${ _('Columns') }',
    'columns': '${ _('columns') }',
    'Compilation': '${ _('Compilation') }',
    'Compute': '${ _('Compute') }',
    'condition': '${ _('condition') }',
    'Confirm History Clearing': '${ _('Confirm History Clearing') }',
    'Confirm the deletion?': '${ _('Confirm the deletion?') }',
    'Connect to the data source': '${ _('Connect to the data source') }',
    'Connect': '${ _('Connect') }',
    'Could not find details for the function': '${_('Could not find details for the function')}',
    'Could not find': '${_('Could not find')}',
    'CPU': '${ _('CPU') }',
    'Create database': '${_('Create database')}',
    'Create Directory': '${_('Create Directory')}',
    'Create folder': '${_('Create folder')}',
    'Create index': '${_('Create index')}',
    'Create table': '${_('Create table')}',
    'Create': '${ _('Create') }',
    'Created': '${ _('Created') }',
    'Created: ': '${ _('Created: ') }',
    'cte': '${ _('cte') }',
    'CTEs': '${ _('CTEs') }',
    'Dashboard': '${ _('Dashboard') }',
    'Data Science': '${ _('Data Science') }',
    'Data Warehouse': '${ _('Data Warehouse') }',
    'Database': '${ _('Database') }',
    'database': '${ _('database') }',
    'Databases': '${ _('Databases') }',
    'default': '${ _('default') }',
    'Delete document': '${ _('Delete document') }',
    'Delete this privilege': '${ _('Delete this privilege') }',
    'Deleting...': '${ _('Deleting...') }',
    'Description': '${ _('Description') }',
    'Details': '${ _('Details') }',
    'Did you mean': '${_('Did you mean')}',
    'dir': '${ _('dir') }',
    'Directory name': '${ _('Directory name') }',
    'Directory': '${ _('Directory') }',
    'DistCp Job': '${_('DistCp Job')}',
    'distinct': '${ _('distinct') }',
    'Do you really want to delete the following document(s)?': '${ _('Do you really want to delete the following document(s)?') }',
    'Document type': '${ _('Document type') }',
    'Documentation': '${ _('Documentation') }',
    'Documents': '${ _('Documents') }',
    'Done. 0 results.': '${ _('Done. 0 results.') }',
    'Done.': '${ _('Done.') }',
    'Drop a SQL file here': '${_('Drop a SQL file here')}',
    'Drop iPython/Zeppelin notebooks here': '${_('Drop iPython/Zeppelin notebooks here')}',
    'Edit list...': '${ _('Edit list...') }',
    'Edit Profile': '${ _('Edit Profile') }',
    'Edit tags': '${ _('Edit tags') }',
    'Edit this privilege': '${ _('Edit this privilege') }',
    'Edit': '${ _('Edit') }',
    'Editor': '${ _('Editor') }',
    'Empty directory': '${ _('Empty directory') }',
    'Empty file...': '${ _('Empty file...') }',
    'Error loading columns.': '${ _('Error loading columns.') }',
    'Error loading contents.': '${ _('Error loading contents.') }',
    'Error loading databases.': '${ _('Error loading databases.') }',
    'Error loading entries': '${ _('Error loading entries') }',
    'Error loading fields.': '${ _('Error loading fields.') }',
    'Error loading index details.': '${ _('Error loading index details.') }',
    'Error loading namespaces.': '${ _('Error loading namespaces.') }',
    'Error loading samples': '${ _('Error loading samples') }',
    'Error loading table details.': '${ _('Error loading table details.') }',
    'Error loading tables.': '${ _('Error loading tables.') }',
    'Error while copying results.': '${ _('Error while copying results.') }',
    'Europe': '${ _('Europe') }',
    'Example: SELECT * FROM tablename, or press CTRL + space': '${ _('Example: SELECT * FROM tablename, or press CTRL + space') }',
    'Execute a query to get query execution analysis.': '${ _('Execute a query to get query execution analysis.') }',
    'Execute': '${ _('Execute') }',
    'Execution': '${ _('Execution') }',
    'Expand to all columns': '${ _('Expand to all columns') }',
    'Expand to selected columns': '${ _('Expand to selected columns') }',
    'Expand': '${ _('Expand') }',
    'Expected end of statement': '${_('Expected end of statement')}',
    'Explain the current SQL query': '${ _('Explain the current SQL query') }',
    'Explain': '${ _('Explain') }',
    'Failed': '${_('Failed')}',
    'Field': '${ _('Field') }',
    'Fields': '${ _('Fields') }',
    'File Browser': '${ _('File Browser') }',
    'Files': '${ _('Files') }',
    'Filter columns...': '${ _('Filter columns...') }',
    'Filter databases...': '${ _('Filter databases...') }',
    'Filter sources...': '${ _('Filter sources...') }',
    'filter': '${ _('filter') }',
    'Filter': '${ _('Filter') }',
    'Filter...': '${ _('Filter...') }',
    'Fix': '${ _('Fix') }',
    'Folder name': '${_('Folder name')}',
    'Foreign key': '${_('Foreign key')}',
    'Foreign keys': '${_('Foreign keys')}',
    'Format the current SQL query': '${ _('Format the current SQL query') }',
    'Share the query selection via a link': '${ _('Share the query selection via a link') }',
    'Share link': '${ _('Share link') }',
    'Share as a gist': '${ _('Share as a gist') }',
    'Format': '${ _('Format') }',
    'France': '${ _('France') }',
    'Functions': '${ _('Functions') }',
    'Germany': '${ _('Germany') }',
    'Get hints on how to port SQL from other databases': '${ _('Get hints on how to port SQL from other databases') }',
    'Go Home': '${_('Go Home')}',
    'Go to column:': '${_('Go to column:')}',
    'Gradient Map': '${ _('Gradient Map') }',
    'Grid': '${ _('Grid') }',
    'group by': '${ _('group by') }',
    'Group': '${ _('Group') }',
    'group': '${ _('group') }',
    'HBase': '${ _('HBase') }',
    'Heatmap': '${ _('Heatmap') }',
    'Help': '${ _('Help') }',
    'Hide advanced': '${_('Hide advanced')}',
    'Hide Details': '${ _('Hide Details') }',
    'Hive Query': '${_('Hive Query')}',
    'Identifiers': '${ _('Identifiers') }',
    'Ignore this type of error': '${_('Ignore this type of error')}',
    'Impala Query': '${_('Impala Query')}',
    'Import complete!': '${ _('Import complete!') }',
    'Import failed!': '${ _('Import failed!') }',
    'Import Hue Documents': '${ _('Import Hue Documents') }',
    'Import Job': '${_('Import Job')}',
    'Import Query History': '${ _('Import Query History') }',
    'Import': '${ _('Import') }',
    'Imported: ': '${ _('Imported: ') }',
    'Importing...': '${ _('Importing...') }',
    'Improve Analysis': '${_('Improve Analysis')}',
    'Indexes': '${ _('Indexes') }',
    'Insert ': '${ _('Insert ') }',
    'Insert at cursor': '${_('Insert at cursor')}',
    'Insert in the editor': '${ _('Insert in the editor') }',
    'Insert value here': '${ _('Insert value here') }',
    'Insert': '${ _('Insert') }',
    'intensity': '${ _('intensity') }',
    'Invalidate all metadata and rebuild index.': '${ _('Invalidate all metadata and rebuild index.') }',
    'IO': '${ _('IO') }',
    'It looks like you are offline or an unknown error happened. Please refresh the page.': '${ _('It looks like you are offline or an unknown error happened. Please refresh the page.') }',
    'Italy': '${ _('Italy') }',
    'Japan': '${ _('Japan') }',
    'Java Job': '${_('Java Job')}',
    'Job browser': '${_('Job browser')}',
    'Job Design': '${_('Job Design')}',
    'Jobs preview': '${_('Jobs preview')}',
    'Jobs': '${_('Jobs')}',
    'join': '${ _('join') }',
    'Key': '${ _('Key') }',
    'keyword': '${ _('keyword') }',
    'Keywords': '${ _('Keywords') }',
    'label': '${ _('label') }',
    'Language Reference': '${ _('Language Reference') }',
    'latitude': '${ _('latitude') }',
    'legend': '${ _('legend') }',
    'Limit the number of results to...': '${ _('Limit the number of results to...') }',
    'limit': '${ _('limit') }',
    'Lines': '${ _('Lines') }',
    'Load recent queries in order to improve recommendations': '${ _('Load recent queries in order to improve recommendations') }',
    'Loading metrics...': '${ _('Loading metrics...') }',
    'Loading...': '${ _('Loading...') }',
    'Lock this row': '${_('Lock this row')}',
    'longitude': '${ _('longitude') }',
    'Manage Users': '${ _('Manage Users') }',
    'Manual refresh': '${_('Manual refresh')}',
    'MapReduce Job': '${_('MapReduce Job')}',
    'Marker Map': '${ _('Marker Map') }',
    'Markers': '${ _('Markers') }',
    'max': '${ _('max') }',
    'Memory': '${ _('Memory') }',
    'Metrics': '${ _('Metrics') }',
    'min': '${ _('min') }',
    'Missing label configuration.': '${ _('Missing label configuration.') }',
    'Missing latitude configuration.': '${ _('Missing latitude configuration.') }',
    'Missing legend configuration.': '${ _('Missing legend configuration.') }',
    'Missing longitude configuration.': '${ _('Missing longitude configuration.') }',
    'Missing region configuration.': '${ _('Missing region configuration.') }',
    'Missing value configuration.': '${ _('Missing value configuration.') }',
    'Missing x axis configuration.': '${ _('Missing x axis configuration.') }',
    'Missing y axis configuration.': '${ _('Missing y axis configuration.') }',
    'Modify': '${ _('Modify') }',
    'More': '${ _('More') }',
    'My Profile': '${ _('My Profile') }',
    'Name': '${ _('Name') }',
    'Namespace': '${ _('Namespace') }',
    'Namespaces': '${ _('Namespaces') }',
    'New document': '${ _('New document') }',
    'New folder': '${ _('New folder') }',
    'No clusters available': '${ _('No clusters available') }',
    'No clusters available.': '${ _('No clusters available.') }',
    'No clusters found': '${ _('No clusters found') }',
    'No columns found': '${ _('No columns found') }',
    'No computes found': '${ _('No computes found') }',
    'No data available': '${ _('No data available') }',
    'No Data Available.': '${ _('No Data Available.') }',
    'No databases found': '${ _('No databases found') }',
    'No databases found.': '${ _('No databases found.') }',
    'No documents found': '${ _('No documents found') }',
    'No entries found': '${ _('No entries found') }',
    'No indexes selected.': '${ _('No indexes selected.') }',
    'No logs available at this moment.': '${ _('No logs available at this moment.') }',
    'No match found': '${ _('No match found') }',
    'No matching records': '${ _('No matching records') }',
    'No namespaces found': '${ _('No namespaces found') }',
    'No namespaces found.': '${ _('No namespaces found.') }',
    'No optimizations identified.': '${ _('No optimizations identified.') }',
    'No privileges found for the selected object.': '${ _('No privileges found for the selected object.') }',
    'No related computes': '${_('No related computes')}',
    'No results found': '${_('No results found')}',
    'No results found.': '${_('No results found.')}',
    'No sorting': '${ _('No sorting') }',
    'No tables available.': '${ _('No tables available.') }',
    'No tables found': '${ _('No tables found') }',
    'No tables identified.': '${ _('No tables identified.') }',
    'No task history.': '${_('Not task history.')}',
    'No': '${ _('No') }',
    'Not available': '${_('Not available')}',
    'Notebook': '${_('Notebook')}',
    'of': '${_('of')}',
    'Oozie Bundle': '${_('Oozie Bundle')}',
    'Oozie Schedule': '${_('Oozie Schedule')}',
    'Oozie Workflow': '${_('Oozie Workflow')}',
    'Open cluster': '${_('Open cluster')}',
    'Open document': '${_('Open document')}',
    'Open folder': '${_('Open folder')}',
    'Open in Browser': '${_('Open in Browser')}',
    'Open in Dashboard': '${_('Open in Dashboard')}',
    'Open in Dashboard...': '${ _('Open in Dashboard...') }',
    'Open in Editor': '${_('Open in Editor')}',
    'Open in File Browser...': '${ _('Open in File Browser...') }',
    'Open in HBase': '${_('Open in HBase')}',
    'Open in Importer': '${_('Open in Importer')}',
    'Open in Table Browser...': '${ _('Open in Table Browser...') }',
    'Open': '${ _('Open') }',
    'Options': '${ _('Options') }',
    'order by': '${ _('order by') }',
    'Order': '${ _('Order') }',
    'other': '${ _('other') }',
    'Output': '${ _('Output') }',
    'Overview': '${ _('Overview') }',
    'Owner': '${ _('Owner') }',
    'Partition key': '${ _('Partition key') }',
    'Partitions': '${ _('Partitions') }',
    'Password': '${ _('Password') }',
    'Permissions': '${ _('Permissions') }',
    'Pie Chart': '${ _('Pie Chart') }',
    'Pig Design': '${_('Pig Design')}',
    'Pig Script': '${_('Pig Script')}',
    'Pin': '${_('Pin')}',
    'Planning': '${ _('Planning') }',
    'Popular': '${ _('Popular') }',
    'Popularity': '${ _('Popularity') }',
    'Preview': '${ _('Preview') }',
    'Primary key': '${ _('Primary key') }',
    'Project': '${ _('Project') }',
    'Queries': '${ _('Queries') }',
    'Query Analysis': '${ _('Query Analysis') }',
    'Query browser': '${ _('Query browser') }',
    'Query failed': '${ _('Query failed') }',
    'Query needs to be saved.': '${ _('Query needs to be saved.') }',
    'Query requires a select or aggregate.': '${ _('Query requires a select or aggregate.') }',
    'Query running': '${ _('Query running') }',
    'Query settings': '${ _('Query settings') }',
    'queued': '${ _('queued') }',
    'Re-create session': '${ _('Re-create session') }',
    'Re-create': '${ _('Re-create') }',
    'Read': '${ _('Read') }',
    'Refresh': '${ _('Refresh') }',
    'region': '${ _('region') }',
    'Remove': '${ _('Remove') }',
    'Replace the editor content...': '${ _('Replace the editor content...') }',
    'Result available': '${ _('Result available') }',
    'Result expired': '${ _('Result expired') }',
    'Result image': '${ _('Result image') }',
    'result(s) copied to the clipboard' : '${ _('result(s) copied to the clipboard') }',
    'Results have expired, rerun the query if needed.': '${ _('Results have expired, rerun the query if needed.') }',
    'Risks': '${ _('Risks') }',
    'Running': '${ _('Running') }',
    'sample query': '${ _('sample query') }',
    'Sample': '${ _('Sample') }',
    'sample': '${ _('sample') }',
    'Samples': '${ _('Samples') }',
    'Save changes': '${ _('Save changes') }',
    'Save session settings as default': '${ _('Save session settings as default') }',
    'Save': '${ _('Save') }',
    'scatter group': '${ _('scatter group') }',
    'Scatter Plot': '${ _('Scatter Plot') }',
    'scatter size': '${ _('scatter size') }',
    'Schedule': '${ _('Schedule') }',
    'scope': '${ _('scope') }',
    'Search Dashboard': '${_('Search Dashboard')}',
    'Search data and saved documents...': '${ _('Search data and saved documents...') }',
    'Search saved documents...': '${_('Search saved documents...')}',
    'Search': '${ _('Search') }',
    'Select a query or start typing to get optimization hints.': '${_('Select a query or start typing to get optimization hints')}',
    'Select and execute a query to see the result.': '${ _('Select and execute a query to see the result.') }',
    'Select json file': '${ _('Select json file') }',
    'Select the chart parameters on the left': '${ _('Select the chart parameters on the left') }',
    'Select this folder': '${_('Select this folder')}',
    'Selected dialect': '${_('Selected dialect')}',
    'Selected entry': '${_('Selected entry')}',
    'Sentry will recursively delete the SERVER or DATABASE privileges you marked for deletion.': '${ _('Sentry will recursively delete the SERVER or DATABASE privileges you marked for deletion.') }',
    'Server': '${ _('Server') }',
    'Sessions': '${ _('Sessions') }',
    'Set as default application': '${_('Set as default application')}',
    'Set as default settings': '${_('Set as default settings')}',
    'Settings': '${ _('Settings') }',
    'Share': '${ _('Share') }',
    'Sharing': '${ _('Sharing') }',
    'Shell Script': '${_('Shell Script')}',
    'Show 50 more...': '${_('Show 50 more...')}',
    'Show advanced': '${_('Show advanced')}',
    'Show columns': '${_('Show columns')}',
    'Show Details': '${ _('Show Details') }',
    'Show details': '${_('Show details')}',
    'Show in Assist...': '${_('Show in Assist...')}',
    'Show more...': '${_('Show more...')}',
    'Show row details': '${_('Show row details')}',
    'Show sample': '${_('Show sample')}',
    'Show view SQL': '${_('Show view SQL')}',
    'Sign out': '${ _('Sign out') }',
    'Size': '${ _('Size') }',
    'Solr Search': '${ _('Solr Search') }',
    'Sort ascending': '${ _('Sort ascending') }',
    'Sort descending': '${ _('Sort descending') }',
    'sorting': '${ _('sorting') }',
    'Sources': '${ _('Sources') }',
    'Spark Job': '${_('Spark Job')}',
    'SQL': '${ _('SQL') }',
    'Start': '${_('Start')}',
    'Starting': '${_('Starting')}',
    'Statement': '${ _('Statement') }',
    'Stats': '${_('Stats')}',
    'Stop batch': '${ _('Stop batch') }',
    'Stop': '${ _('Stop') }',
    'Stopped': '${_('Stopped')}',
    'Stopping': '${ _('Stopping') }',
    'Streams': '${ _('Streams') }',
    'Success.': '${ _('Success.') }',
    'Summary': '${_('Summary')}',
    'Table Browser': '${ _('Table Browser') }',
    'table': '${ _('table') }',
    'Table': '${ _('Table') }',
    'Tables': '${ _('Tables') }',
    'Tags can only contain 1 to 50 alphanumeric characters, _ or -.': '${ _('Tags can only contain 1 to 50 alphanumeric characters, _ or -.') }',
    'Tags could not be loaded.': '${ _('Tags could not be loaded.') }',
    'Task History': '${ _('Task History') }',
    'Terms': '${ _('Terms') }',
    'The document is not shared for modify.': '${ _('The document is not shared for modify.') }',
    'The document is not shared for read.': '${ _('The document is not shared for read.') }',
    'The file has not been found': '${_('The file has not been found')}',
    'The table has no columns': '${_('The table has no columns')}',
    'The trash is empty': '${_('The trash is empty')}',
    'The upload has been canceled': '${ _('The upload has been canceled') }',
    'There are currently no information about the sessions.': '${ _('There are currently no information about the sessions.') }',
    'There are no stats to be shown': '${ _('There are no stats to be shown') }',
    'There are no terms to be shown': '${ _('There are no terms to be shown') }',
    'There is currently no information about the sessions.': '${ _('There is currently no information about the sessions.') }',
    'There was a problem loading the databases': '${ _('There was a problem loading the databases') }',
    'There was a problem loading the index preview': '${ _('There was a problem loading the index preview') }',
    'There was a problem loading the indexes': '${ _('There was a problem loading the indexes') }',
    'There was a problem loading the table preview': '${ _('There was a problem loading the table preview') }',
    'There was an error loading the document.': '${ _('There was an error loading the document.') }',
    'This field does not support stats': '${ _('This field does not support stats') }',
    'This will sync missing tables.': '${ _('This will sync missing tables.') }',
    'Timeline Chart': '${ _('Timeline Chart') }',
    'Timeline': '${ _('Timeline') }',
    'Top down analysis': '${ _('Top down analysis') }',
    'Top Nodes': '${ _('Top Nodes') }',
    'Topics': '${ _('Topics') }',
    'Type a username or a group name': '${ _('Type a username or a group name') }',
    'Type': '${ _('Type') }',
    'type': '${ _('type') }',
    'UDFs': '${ _('UDFs') }',
    'UK': '${ _('UK') }',
    'Undo': '${ _('Undo') }',
    'Unlock this row': '${_('Unlock this row')}',
    'Unset from default application': '${_('Unset from default application')}',
    'Updated: ': '${ _('Updated: ') }',
    'Upload a file': '${_('Upload a file')}',
    'Upload file': '${_('Upload file')}',
    'Upload optimizer history': '${ _('Upload optimizer history') }',
    'uploaded successfully': '${ _('uploaded successfully') }',
    'USA': '${ _('USA') }',
    'used by': '${ _('used by') }',
    'Username': '${ _('Username') }',
    'Value': '${ _('Value') }',
    'value': '${ _('value') }',
    'Values': '${ _('Values') }',
    'variable': '${ _('variable') }',
    'Variables': '${ _('Variables') }',
    'View Profile': '${ _('View Profile') }',
    'View': '${ _('View') }',
    'view': '${ _('view') }',
    'Views': '${ _('Views') }',
    'virtual': '${ _('virtual') }',
    'Welcome Tour': '${ _('Welcome Tour') }',
    'With grant option': '${ _('With grant option') }',
    'With grant': '${ _('With grant') }',
    'Workflow': '${ _('Workflow') }',
    'World': '${ _('World') }',
    'x-axis': '${ _('x-axis') }',
    'y-axis': '${ _('y-axis') }',
    'Yes': '${ _('Yes') }',
    'Yes, delete': '${ _('Yes, delete') }',
  };

  window.STATIC_URLS = {
    'desktop/art/cloudera-data-warehouse-3.svg': '${ static('desktop/art/cloudera-data-warehouse-3.svg') }',
    'beeswax/art/icon_beeswax_48.png': '${ static('beeswax/art/icon_beeswax_48.png') }',
    'impala/art/icon_impala_48.png': '${ static('impala/art/icon_impala_48.png') }',
  };

  window.HUE_VERSION = '${ hue_version() }';

  %if hasattr(ENABLE_NEW_INDEXER, 'get') and ENABLE_NEW_INDEXER.get():
    window.IS_NEW_INDEXER_ENABLED = true;
  %else:
    window.IS_NEW_INDEXER_ENABLED = false;
  %endif

  window.IS_S3_ENABLED = '${ is_s3_enabled }' === 'True';

  window.LEAFLET_DEFAULTS = {
    layer: '${ leaflet['layer'] |n,unicode }',
    attribution: '${ leaflet['attribution'] |n,unicode }',
    mapOptions: JSON.parse('${ leaflet['map_options'] |n,unicode }'),
    layerOptions: JSON.parse('${ leaflet['layer_options'] |n,unicode }'),
    images: {
      'icon': '${ static('desktop/ext/img/leaflet/marker-icon.png') }',
      'icon-2x': '${ static('desktop/ext/img/leaflet/marker-icon-2x.png') }',
      'shadow': '${ static('desktop/ext/img/leaflet/marker-shadow.png') }',
    }
  };

  window.USER_VIEW_EDIT_USER_ENABLED = '${ user.has_hue_permission(action="access_view:useradmin:edit_user", app="useradmin") or is_admin(user) }' === 'True';
  window.USER_IS_ADMIN = '${ is_admin(user) }' === 'True';
  window.USER_IS_HUE_ADMIN = '${ is_hue_admin(user) }' === 'True';
  window.DJANGO_DEBUG_MODE = '${ conf.DJANGO_DEBUG_MODE.get() }' === 'True';
  window.IS_LDAP_SETUP = '${ 'desktop.auth.backend.LdapBackend' in conf.AUTH.BACKEND.get() }' === 'True';
  window.LOGGED_USERNAME = '${ user.username }';
  window.LOGGED_USER_ID = ${ user.id };

  <%
    # TODO remove
    # Code moved from assist.mako
    try:
      home_dir = REMOTE_STORAGE_HOME.get() if hasattr(REMOTE_STORAGE_HOME, 'get') and REMOTE_STORAGE_HOME.get() else user.get_home_directory()
      if not request.fs.isdir(home_dir):
        home_dir = '/'
    except:
      home_dir = '/'
  %>

  window.USE_NEW_SIDE_PANELS = '${ USE_NEW_SIDE_PANELS.get() }' === 'True'
  window.USER_HOME_DIR = '${ home_dir }';

  var userGroups = [];
  % for group in user.groups.all():
    userGroups.push('${ group }');
  % endfor
  window.LOGGED_USERGROUPS = userGroups;

  var hueApps = [];
  % for app in apps:
    hueApps.push('${ app }')
  % endfor
  window.HUE_APPS = hueApps;

  window.METASTORE_PARTITION_LIMIT = ${ hasattr(LIST_PARTITIONS_LIMIT, 'get') and LIST_PARTITIONS_LIMIT.get() or 1000 };

  window.SQL_COLUMNS_KNOWN_FACET_VALUES = {
    'type': { 'array': -1, 'boolean': -1, 'bigint': -1, 'binary': -1, 'char': -1, 'date': -1, 'double': -1,
      'decimal': -1, 'float': -1, 'int': -1, 'map': -1, 'real': -1, 'smallint': -1, 'string': -1, 'struct': -1,
      'timestamp': -1, 'tinyint': -1, 'varchar': -1 }
  };

  window.SQL_ASSIST_KNOWN_FACET_VALUES = {
    'type': {'array': -1, 'table': -1, 'view': -1, 'boolean': -1, 'bigint': -1, 'binary': -1, 'char': -1, 'date': -1, 'double': -1, 'decimal': -1, 'float': -1, 'int': -1, 'map': -1, 'real': -1, 'smallint': -1, 'string': -1, 'struct': -1, 'timestamp': -1, 'tinyint': -1, 'varchar': -1 }
  };

  window.SOLR_ASSIST_KNOWN_FACET_VALUES = {
    'type': {'date': -1, 'tdate': -1, 'timestamp': -1, 'pdate': -1, 'int': -1, 'tint': -1, 'pint': -1, 'long': -1, 'tlong': -1, 'plong': -1, 'float': -1, 'tfloat': -1, 'pfloat': -1, 'double': -1, 'tdouble': -1, 'pdouble': -1, 'currency': -1, 'smallint': -1, 'bigint': -1, 'tinyint': -1, 'SpatialRecursivePrefixTreeFieldType': -1, 'string': -1, 'boolean': -1 }
  };

  window.WEB_SOCKETS_ENABLED = window.WebSocket && '${ has_channels() }' === 'True';

  ${ sqlDocIndex.sqlDocIndex() }
  ${ sqlDocIndex.sqlDocTopLevel() }
})();
