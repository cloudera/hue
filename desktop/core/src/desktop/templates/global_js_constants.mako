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
  from desktop.conf import IS_EMBEDDED, IS_K8S_ONLY, IS_MULTICLUSTER_ONLY
  from desktop.models import hue_version

  from beeswax.conf import LIST_PARTITIONS_LIMIT
  from indexer.conf import ENABLE_NEW_INDEXER
  from metadata.conf import has_navigator, has_optimizer, has_workload_analytics, OPTIMIZER
  from notebook.conf import ENABLE_QUERY_ANALYSIS
%>

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

  window.HAS_MULTI_CLUSTER = '${ conf.has_multi_cluster() }' === 'True';

  window.DROPZONE_HOME_DIR = '${ user.get_home_directory() if not user.is_anonymous() else "" }';

  window.ENABLE_SQL_SYNTAX_CHECK = '${ conf.ENABLE_SQL_SYNTAX_CHECK.get() }' === 'True';

  window.HAS_NAVIGATOR = '${ has_navigator(request.user) }' === 'True';

  window.HAS_OPTIMIZER = '${ has_optimizer() }' === 'True';

  ## In the past was has_workload_analytics()
  window.HAS_WORKLOAD_ANALYTICS = '${ ENABLE_QUERY_ANALYSIS.get() }' === 'True';

  window.HUE_CONTAINER = '${ IS_EMBEDDED.get() }' === 'True' ? '.hue-embedded-container' : 'body';

  window.IS_MULTICLUSTER_ONLY = '${ IS_MULTICLUSTER_ONLY.get() }' === 'True';
  window.IS_EMBEDDED = '${ IS_EMBEDDED.get() }' === 'True';
  window.IS_K8S_ONLY = '${ IS_K8S_ONLY.get() }' === 'True';
  window.JB_HEADER_CHECK_INTERVAL_IN_MILLIS = 30000;
  window.JB_SINGLE_CHECK_INTERVAL_IN_MILLIS = 5000;
  window.JB_MULTI_CHECK_INTERVAL_IN_MILLIS = 20000;

  // TODO: Replace with json import
  window.HUE_I18n = {
    'Add more...': '${ _('Add more...') }',
    'aggregate': '${ _('aggregate') }',
    'alias': '${ _('alias') }',
    'All': '${_('All')}',
    'An error occurred refreshing the table stats. Please try again.': '${_('An error occurred refreshing the table stats. Please try again.')}',
    'Apps': '${ _('Apps') }',
    'Back': '${_('Back')}',
    'Browsers': '${ _('Browsers') }',
    'Cancel upload': '${ _('Cancel upload') }',
    'Cancel': '${_('Cancel')}',
    'Choose...': '${ _('Choose...') }',
    'CodeGen': '${ _('CodeGen') }',
    'column name...': '${_('column name...')}',
    'Columns': '${ _('Columns') }',
    'Compilation': '${ _('Compilation') }',
    'condition': '${ _('condition') }',
    'Could not find': '${_('Could not find')}',
    'CPU': '${ _('CPU') }',
    'Create folder': '${_('Create folder')}',
    'cte': '${ _('cte') }',
    'CTEs': '${ _('CTEs') }',
    'database': '${ _('database') }',
    'Databases': '${ _('Databases') }',
    'Did you mean': '${_('Did you mean')}',
    'dir': '${ _('dir') }',
    'Directory': '${ _('Directory') }',
    'DistCp Job': '${_('DistCp Job')}',
    'Documents': '${ _('Documents') }',
    'Drop a SQL file here': '${_('Drop a SQL file here')}',
    'Drop iPython/Zeppelin notebooks here': '${_('Drop iPython/Zeppelin notebooks here')}',
    'Edit tags': '${ _('Edit tags') }',
    'Editor': '${ _('Editor') }',
    'Error while copying results.': '${ _('Error while copying results.') }',
    'Execution': '${ _('Execution') }',
    'Expected end of statement': '${_('Expected end of statement')}',
    'Failed': '${_('Failed')}',
    'Fields': '${ _('Fields') }',
    'Files': '${ _('Files') }',
    'filter': '${ _('filter') }',
    'Folder name': '${_('Folder name')}',
    'Functions': '${ _('Functions') }',
    'Go to column:': '${_('Go to column:')}',
    'group by': '${ _('group by') }',
    'Hive Query': '${_('Hive Query')}',
    'Identifiers': '${ _('Identifiers') }',
    'Ignore this type of error': '${_('Ignore this type of error')}',
    'Impala Query': '${_('Impala Query')}',
    'Import Job': '${_('Import Job')}',
    'Insert value here': '${ _('Insert value here') }',
    'IO': '${ _('IO') }',
    'It looks like you are offline or an unknown error happened. Please refresh the page.': '${ _('It looks like you are offline or an unknown error happened. Please refresh the page.') }',
    'Java Job': '${_('Java Job')}',
    'Job Design': '${_('Job Design')}',
    'join': '${ _('join') }',
    'keyword': '${ _('keyword') }',
    'Keywords': '${ _('Keywords') }',
    'Lock this row': '${_('Lock this row')}',
    'MapReduce Job': '${_('MapReduce Job')}',
    'Metrics': '${ _('Metrics') }',
    'Missing label configuration.': '${ _('Missing label configuration.') }',
    'Missing latitude configuration.': '${ _('Missing latitude configuration.') }',
    'Missing legend configuration.': '${ _('Missing legend configuration.') }',
    'Missing longitude configuration.': '${ _('Missing longitude configuration.') }',
    'Missing region configuration.': '${ _('Missing region configuration.') }',
    'Missing value configuration.': '${ _('Missing value configuration.') }',
    'Missing x axis configuration.': '${ _('Missing x axis configuration.') }',
    'Missing y axis configuration.': '${ _('Missing y axis configuration.') }',
    'No Data Available.': '${ _('No Data Available.') }',
    'No results found.': '${_('No results found.')}',
    'Notebook': '${_('Notebook')}',
    'of': '${_('of')}',
    'Oozie Bundle': '${_('Oozie Bundle')}',
    'Oozie Schedule': '${_('Oozie Schedule')}',
    'Oozie Workflow': '${_('Oozie Workflow')}',
    'Options': '${ _('Options') }',
    'order by': '${ _('order by') }',
    'Overview': '${ _('Overview') }',
    'Pig Design': '${_('Pig Design')}',
    'Pig Script': '${_('Pig Script')}',
    'Planning': '${ _('Planning') }',
    'Popular': '${ _('Popular') }',
    'Query requires a select or aggregate.': '${ _('Query requires a select or aggregate.') }',
    'result(s) copied to the clipboard' : '${ _('result(s) copied to the clipboard') }',
    'Risks': '${ _('Risks') }',
    'sample': '${ _('sample') }',
    'Samples': '${ _('Samples') }',
    'Search Dashboard': '${_('Search Dashboard')}',
    'Select this folder': '${_('Select this folder')}',
    'Shell Script': '${_('Shell Script')}',
    'Show row details': '${_('Show row details')}',
    'Spark Job': '${_('Spark Job')}',
    'table': '${ _('table') }',
    'Tables': '${ _('Tables') }',
    'The file has not been found': '${_('The file has not been found')}',
    'The upload has been canceled': '${ _('The upload has been canceled') }',
    'Timeline': '${ _('Timeline') }',
    'Top Nodes': '${ _('Top Nodes') }',
    'UDFs': '${ _('UDFs') }',
    'Unlock this row': '${_('Unlock this row')}',
    'Upload a file': '${_('Upload a file')}',
    'uploaded successfully': '${ _('uploaded successfully') }',
    'variable': '${ _('variable') }',
    'Variables': '${ _('Variables') }',
    'view': '${ _('view') }',
    'virtual': '${ _('virtual') }'
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

  window.USER_HOME_DIR = '${ user.get_home_directory() }';

  var userGroups = [];
  % for group in user.groups.all():
    userGroups.push('${ group }');
  % endfor

  window.LOGGED_USERGROUPS = userGroups;

  window.METASTORE_PARTITION_LIMIT = ${ hasattr(LIST_PARTITIONS_LIMIT, 'get') and LIST_PARTITIONS_LIMIT.get() or 1000 };

  window.SQL_COLUMNS_KNOWN_FACET_VALUES = {
    'type': { 'array': -1, 'boolean': -1, 'bigint': -1, 'binary': -1, 'char': -1, 'date': -1, 'double': -1,
      'decimal': -1, 'float': -1, 'int': -1, 'map': -1, 'real': -1, 'smallint': -1, 'string': -1, 'struct': -1,
      'timestamp': -1, 'tinyint': -1, 'varchar': -1 }
  };
})();