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
  from desktop.conf import IS_EMBEDDED, IS_K8S_ONLY, IS_MULTICLUSTER_ONLY, USE_NEW_SIDE_PANELS, VCS
  from desktop.models import hue_version, _get_apps

  from beeswax.conf import LIST_PARTITIONS_LIMIT
  from dashboard.conf import HAS_SQL_ENABLED
  from filebrowser.conf import SHOW_UPLOAD_BUTTON
  from indexer.conf import ENABLE_NEW_INDEXER
  from metadata.conf import has_catalog, has_readonly_catalog, has_optimizer, has_workload_analytics, OPTIMIZER
  from metastore.conf import ENABLE_NEW_CREATE_TABLE
  from notebook.conf import ENABLE_NOTEBOOK_2, ENABLE_QUERY_ANALYSIS, ENABLE_QUERY_BUILDER, ENABLE_QUERY_SCHEDULING, get_ordered_interpreters, SHOW_NOTEBOOKS

  from metastore.views import has_write_access
%>

<%namespace name="sqlDocIndex" file="/sql_doc_index.mako" />

(function () {
  window.AUTOCOMPLETE_TIMEOUT = ${ conf.EDITOR_AUTOCOMPLETE_TIMEOUT.get() };

  window.BANNER_TOP_HTML = '${ conf.CUSTOM.BANNER_TOP_HTML.get() }';

  window.CACHEABLE_TTL = {
    default: ${ conf.CUSTOM.CACHEABLE_TTL.get() },
    optimizer: ${ OPTIMIZER.CACHEABLE_TTL.get() }
  };

  window.DEV = '${ conf.DEV.get() }' === 'True';

  %if request and request.COOKIES and request.COOKIES.get('csrftoken', '') != '':
    window.CSRF_TOKEN = '${request.COOKIES.get('csrftoken')}';
  %else:
    window.CSRF_TOKEN = '';
  %endif

  window.KNOX_BASE_PATH_HUE = '/KNOX_BASE_PATH_HUE';
  window._KNOX_BASE_PATH = '/KNOX_BASE_PATH_KNOX';
  window._KNOX_BASE_URL = '/KNOX_BASE_URL';
  window.HUE_BASE_URL = window.KNOX_BASE_PATH_HUE.indexOf('KNOX_BASE_PATH_HUE') < 0 ? window.KNOX_BASE_PATH_HUE : '';
  window.KNOX_BASE_PATH = window._KNOX_BASE_PATH.indexOf('KNOX_BASE_PATH_KNOX') < 0 ? window._KNOX_BASE_PATH_KNOX : '';
  window.KNOX_BASE_URL = window._KNOX_BASE_URL.indexOf('KNOX_BASE_URL') < 0 ? window._KNOX_BASE_URL : '';

  window.HAS_GIT = ${ len(VCS.keys()) } > 0;
  window.HAS_MULTI_CLUSTER = '${ conf.has_multi_cluster() }' === 'True';
  window.HAS_SQL_DASHBOARD = '${ HAS_SQL_ENABLED.get() }' === 'True';

  window.DROPZONE_HOME_DIR = '${ user.get_home_directory() if not user.is_anonymous() else "" }';

  window.USER_HAS_METADATA_WRITE_PERM = '${ user.has_hue_permission(action="write", app="metadata") }' === 'True';

  window.ENABLE_NEW_CREATE_TABLE = '${ hasattr(ENABLE_NEW_CREATE_TABLE, 'get') and ENABLE_NEW_CREATE_TABLE.get()}' === 'True';
  window.ENABLE_NOTEBOOK_2 = '${ ENABLE_NOTEBOOK_2.get() }' === 'True';

  window.ENABLE_QUERY_BUILDER = '${ ENABLE_QUERY_BUILDER.get() }' === 'True';
  window.ENABLE_QUERY_SCHEDULING = '${ ENABLE_QUERY_SCHEDULING.get() }' === 'True';

  window.ENABLE_SQL_SYNTAX_CHECK = '${ conf.ENABLE_SQL_SYNTAX_CHECK.get() }' === 'True';

  window.HAS_CATALOG = '${ has_catalog(request.user) }' === 'True';
  window.HAS_READ_ONLY_CATALOG = '${ has_readonly_catalog(request.user) }' === 'True' || '${ has_write_access(request.user) }' === 'False';

  window.HAS_OPTIMIZER = '${ has_optimizer() }' === 'True';

  ## In the past was has_workload_analytics()
  window.HAS_WORKLOAD_ANALYTICS = '${ ENABLE_QUERY_ANALYSIS.get() }' === 'True';

  window.HUE_CONTAINER = '${ IS_EMBEDDED.get() }' === 'True' ? '.hue-embedded-container' : 'body';

  window.SHOW_NOTEBOOKS = '${ SHOW_NOTEBOOKS.get() }' === 'True'
  window.SHOW_UPLOAD_BUTTON = '${ hasattr(SHOW_UPLOAD_BUTTON, 'get') and SHOW_UPLOAD_BUTTON.get() }' === 'True'

  window.IS_MULTICLUSTER_ONLY = '${ IS_MULTICLUSTER_ONLY.get() }' === 'True';
  window.IS_EMBEDDED = '${ IS_EMBEDDED.get() }' === 'True';
  window.IS_K8S_ONLY = '${ IS_K8S_ONLY.get() }' === 'True';
  window.JB_HEADER_CHECK_INTERVAL_IN_MILLIS = 30000;
  window.JB_SINGLE_CHECK_INTERVAL_IN_MILLIS = 5000;
  window.JB_MULTI_CHECK_INTERVAL_IN_MILLIS = 20000;


  window.HUE_URLS = {
    IMPORTER_CREATE_TABLE: '${url('indexer:importer_prefill', source_type = 'all', target_type = 'table')}',
    IMPORTER_CREATE_DATABASE: '${url('indexer:importer_prefill', source_type = 'manual', target_type = 'database')}',
    NOTEBOOK_INDEX: '${url('notebook:index')}',
    PIG_INDEX: '${url('pig:index')}',
    OOZIE_NEW_WORKFLOW: '${url('oozie:new_workflow')}',
    OOZIE_NEW_COORDINATOR: '${url('oozie:new_coordinator')}',
    OOZIE_NEW_BUNDLE: '${url('oozie:new_bundle')}',
    SEARCH_NEW_SEARCH: '${url('search:new_search')}',
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
    'Add more...': '${ _('Add more...') }',
    'Add privilege': '${ _('Add privilege') }',
    'Add properties...': '${ _('Add properties...') }',
    'Add tags...': '${ _('Add tags...') }',
    'Add': '${ _('Add') }',
    'Admin': '${ _('Admin') }',
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
    'at cursor': '${ _('at cursor') }',
    'Back': '${_('Back')}',
    'Browse column privileges': '${_('Browse column privileges')}',
    'Browse DB privileges': '${_('Browse DB privileges')}',
    'Browse table privileges': '${_('Browse table privileges')}',
    'Browsers': '${ _('Browsers') }',
    'Cancel upload': '${ _('Cancel upload') }',
    'Cancel': '${_('Cancel')}',
    'Choose...': '${ _('Choose...') }',
    'Clear cache': '${ _('Clear cache') }',
    'Clear the query history': '${ _('Clear the query history') }',
    'Click for more details': '${ _('Click for more details') }',
    'Close': '${_('Close')}',
    'Cluster': '${ _('Cluster') }',
    'Clusters': '${ _('Clusters') }',
    'CodeGen': '${ _('CodeGen') }',
    'Collection': '${ _('Collection') }',
    'column name...': '${_('column name...')}',
    'Column': '${ _('Column') }',
    'Columns': '${ _('Columns') }',
    'Compilation': '${ _('Compilation') }',
    'Compute': '${ _('Compute') }',
    'condition': '${ _('condition') }',
    'Confirm History Clearing': '${ _('Confirm History Clearing') }',
    'Confirm the deletion?': '${ _('Confirm the deletion?') }',
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
    'Documents': '${ _('Documents') }',
    'Drop a SQL file here': '${_('Drop a SQL file here')}',
    'Drop iPython/Zeppelin notebooks here': '${_('Drop iPython/Zeppelin notebooks here')}',
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
    'Error loading namespaces.': '${ _('Error loading namespaces.') }',
    'Error loading samples': '${ _('Error loading samples') }',
    'Error loading tables.': '${ _('Error loading tables.') }',
    'Error while copying results.': '${ _('Error while copying results.') }',
    'Example: SELECT * FROM tablename, or press CTRL + space': '${ _('Example: SELECT * FROM tablename, or press CTRL + space') }',
    'Execute a query to get query execution analysis.': '${ _('Execute a query to get query execution analysis.') }',
    'Execution': '${ _('Execution') }',
    'Expand to all columns': '${ _('Expand to all columns') }',
    'Expand to selected columns': '${ _('Expand to selected columns') }',
    'Expected end of statement': '${_('Expected end of statement')}',
    'Failed': '${_('Failed')}',
    'Field': '${ _('Field') }',
    'Fields': '${ _('Fields') }',
    'File Browser': '${ _('File Browser') }',
    'Files': '${ _('Files') }',
    'Filter databases...': '${ _('Filter databases...') }',
    'Filter sources...': '${ _('Filter sources...') }',
    'filter': '${ _('filter') }',
    'Filter': '${ _('Filter') }',
    'Filter...': '${ _('Filter...') }',
    'Fix': '${ _('Fix') }',
    'Folder name': '${_('Folder name')}',
    'Foreign key': '${_('Foreign key')}',
    'Foreign keys': '${_('Foreign keys')}',
    'Functions': '${ _('Functions') }',
    'Go Home': '${_('Go Home')}',
    'Go to column:': '${_('Go to column:')}',
    'group by': '${ _('group by') }',
    'Heatmap': '${ _('Heatmap') }',
    'Hide advanced': '${_('Hide advanced')}',
    'Hive Query': '${_('Hive Query')}',
    'Identifiers': '${ _('Identifiers') }',
    'Ignore this type of error': '${_('Ignore this type of error')}',
    'Impala Query': '${_('Impala Query')}',
    'Import Job': '${_('Import Job')}',
    'Indexes': '${ _('Indexes') }',
    'Insert at cursor': '${_('Insert at cursor')}',
    'Insert in the editor': '${ _('Insert in the editor') }',
    'Insert value here': '${ _('Insert value here') }',
    'Insert': '${ _('Insert') }',
    'Invalidate all metadata and rebuild index.': '${ _('Invalidate all metadata and rebuild index.') }',
    'IO': '${ _('IO') }',
    'It looks like you are offline or an unknown error happened. Please refresh the page.': '${ _('It looks like you are offline or an unknown error happened. Please refresh the page.') }',
    'Java Job': '${_('Java Job')}',
    'Job browser': '${_('Job browser')}',
    'Job Design': '${_('Job Design')}',
    'Jobs preview': '${_('Jobs preview')}',
    'Jobs': '${_('Jobs')}',
    'join': '${ _('join') }',
    'Key': '${ _('Key') }',
    'keyword': '${ _('keyword') }',
    'Keywords': '${ _('Keywords') }',
    'Loading metrics...': '${ _('Loading metrics...') }',
    'Lock this row': '${_('Lock this row')}',
    'MapReduce Job': '${_('MapReduce Job')}',
    'Manual refresh': '${_('Manual refresh')}',
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
    'Name': '${ _('Name') }',
    'Namespace': '${ _('Namespace') }',
    'Namespaces': '${ _('Namespaces') }',
    'New document': '${ _('New document') }',
    'New folder': '${ _('New folder') }',
    'No clusters available': '${ _('No clusters available') }',
    'No clusters found': '${ _('No clusters found') }',
    'No columns found': '${ _('No columns found') }',
    'No computes found': '${ _('No computes found') }',
    'No Data Available.': '${ _('No Data Available.') }',
    'No databases found': '${ _('No databases found') }',
    'No databases found.': '${ _('No databases found.') }',
    'No documents found': '${ _('No documents found') }',
    'No entries found': '${ _('No entries found') }',
    'No logs available at this moment.': '${ _('No logs available at this moment.') }',
    'No match found': '${ _('No match found') }',
    'No namespaces found': '${ _('No namespaces found') }',
    'No namespaces found.': '${ _('No namespaces found.') }',
    'No privileges found for the selected object.': '${ _('No privileges found for the selected object.') }',
    'No results found': '${_('No results found')}',
    'No results found.': '${_('No results found.')}',
    'No tables available.': '${ _('No tables available.') }',
    'No tables found': '${ _('No tables found') }',
    'No task history.': '${_('Not task history.')}',
    'No': '${ _('No') }',
    'No related computes': '${_('No related computes')}',
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
    'Open in HBase': '${_('Open in HBase')}',
    'Open in Importer': '${_('Open in Importer')}',
    'Open in File Browser...': '${ _('Open in File Browser...') }',
    'Open in Table Browser...': '${ _('Open in Table Browser...') }',
    'Open': '${ _('Open') }',
    'Options': '${ _('Options') }',
    'Order': '${ _('Order') }',
    'order by': '${ _('order by') }',
    'other': '${ _('other') }',
    'Output': '${ _('Output') }',
    'Overview': '${ _('Overview') }',
    'Owner': '${ _('Owner') }',
    'Partition key': '${ _('Partition key') }',
    'Partitions': '${ _('Partitions') }',
    'Perform incremental metadata update.': '${ _('Perform incremental metadata update.') }',
    'Permissions': '${ _('Permissions') }',
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
    'Query browser': '${ _('Query browser') }',
    'Query failed': '${ _('Query failed') }',
    'Query requires a select or aggregate.': '${ _('Query requires a select or aggregate.') }',
    'Query running': '${ _('Query running') }',
    'queued': '${ _('queued') }',
    'Refresh': '${ _('Refresh') }',
    'Remove': '${ _('Remove') }',
    'Replace the editor content...': '${ _('Replace the editor content...') }',
    'Result available': '${ _('Result available') }',
    'Result expired': '${ _('Result expired') }',
    'result(s) copied to the clipboard' : '${ _('result(s) copied to the clipboard') }',
    'Risks': '${ _('Risks') }',
    'sample query': '${ _('sample query') }',
    'Sample': '${ _('Sample') }',
    'sample': '${ _('sample') }',
    'Samples': '${ _('Samples') }',
    'Save': '${ _('Save') }',
    'Schedule': '${ _('Schedule') }',
    'Search Dashboard': '${_('Search Dashboard')}',
    'Search data and saved documents...': '${ _('Search data and saved documents...') }',
    'Search saved documents...': '${_('Search saved documents...')}',
    'Select this folder': '${_('Select this folder')}',
    'Selected entry': '${_('Selected entry')}',
    'Sentry will recursively delete the SERVER or DATABASE privileges you marked for deletion.': '${ _('Sentry will recursively delete the SERVER or DATABASE privileges you marked for deletion.') }',
    'Server': '${ _('Server') }',
    'Set as default application': '${_('Set as default application')}',
    'Shell Script': '${_('Shell Script')}',
    'Show 50 more...': '${_('Show 50 more...')}',
    'Show advanced': '${_('Show advanced')}',
    'Show columns': '${_('Show columns')}',
    'Show details': '${_('Show details')}',
    'Show in Assist...': '${_('Show in Assist...')}',
    'Show more...': '${_('Show more...')}',
    'Show row details': '${_('Show row details')}',
    'Show sample': '${_('Show sample')}',
    'Show view SQL': '${_('Show view SQL')}',
    'Size': '${ _('Size') }',
    'Solr Search': '${ _('Solr Search') }',
    'Sources': '${ _('Sources') }',
    'Spark Job': '${_('Spark Job')}',
    'Starting': '${_('Starting')}',
    'Stats': '${_('Stats')}',
    'Summary': '${_('Summary')}',
    'Table Browser': '${ _('Table Browser') }',
    'table': '${ _('table') }',
    'Table': '${ _('Table') }',
    'Tables': '${ _('Tables') }',
    'Tags can only contain 1 to 50 alphanumeric characters, _ or -.': '${ _('Tags can only contain 1 to 50 alphanumeric characters, _ or -.') }',
    'Tags could not be loaded.': '${ _('Tags could not be loaded.') }',
    'Task History': '${ _('Task History') }',
    'Terms': '${ _('Terms') }',
    'The file has not been found': '${_('The file has not been found')}',
    'The table has no columns': '${_('The table has no columns')}',
    'The trash is empty': '${_('The trash is empty')}',
    'The upload has been canceled': '${ _('The upload has been canceled') }',
    'There are no stats to be shown': '${ _('There are no stats to be shown') }',
    'There are no terms to be shown': '${ _('There are no terms to be shown') }',
    'This field does not support stats': '${ _('This field does not support stats') }',
    'This will sync missing tables.': '${ _('This will sync missing tables.') }',
    'Timeline': '${ _('Timeline') }',
    'Top down analysis': '${ _('Top down analysis') }',
    'Top Nodes': '${ _('Top Nodes') }',
    'Topics': '${ _('Topics') }',
    'Type': '${ _('Type') }',
    'UDFs': '${ _('UDFs') }',
    'Undo': '${ _('Undo') }',
    'Unlock this row': '${_('Unlock this row')}',
    'Unset from default application': '${_('Unset from default application')}',
    'Upload a file': '${_('Upload a file')}',
    'Upload file': '${_('Upload file')}',
    'uploaded successfully': '${ _('uploaded successfully') }',
    'used by': '${ _('used by') }',
    'Value': '${ _('Value') }',
    'Values': '${ _('Values') }',
    'variable': '${ _('variable') }',
    'Variables': '${ _('Variables') }',
    'view': '${ _('view') }',
    'Views': '${ _('Views') }',
    'virtual': '${ _('virtual') }',
    'WARNING: This can be both resource and time-intensive.': '${ _('WARNING: This can be both resource and time-intensive.') }',
    'With grant option': '${ _('With grant option') }',
    'With grant': '${ _('With grant') }',
    'Workflow': '${ _('Workflow') }',
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
    layerOptions: JSON.parse('${ leaflet['layer_options'] |n,unicode }')
  };

  window.LOGGED_USERNAME = '${ user.username }';
  window.LOGGED_USER_ID = ${ user.id };

  <%
    # TODO remove
    # Code moved from assist.mako
    try:
      home_dir = user.get_home_directory()
      if not request.fs.isdir(home_dir):
        home_dir = '/'
    except:
      home_dir = '/'
  %>

  window.USE_NEW_SIDE_PANELS = '${ USE_NEW_SIDE_PANELS.get() }' === 'True'
  window.USER_HOME_DIR = '${ home_dir }';

  // TODO: Refactor assist to fetch from config.
  window.ASSIST_SQL_INTERPRETERS = [];
  % for interpreter in get_ordered_interpreters(request.user):
    % if interpreter["is_sql"]:
      ASSIST_SQL_INTERPRETERS.push({
        type: '${ interpreter["type"] }',
        name: '${ interpreter["name"] }'
      });
    % endif
  % endfor

  var userGroups = [];
  % for group in user.groups.all():
    userGroups.push('${ group }');
  % endfor
  window.LOGGED_USERGROUPS = userGroups;

  var hueApps = [];
  % for app in _get_apps(request.user, ''):
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

  ${ sqlDocIndex.sqlDocIndex() }
})();
