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
  from desktop.conf import IS_EMBEDDED
  from desktop.models import hue_version

  from beeswax.conf import LIST_PARTITIONS_LIMIT
  from indexer.conf import ENABLE_NEW_INDEXER
  from metadata.conf import has_navigator, has_optimizer, has_workload_analytics, OPTIMIZER
%>

(function () {
  window.AUTOCOMPLETE_TIMEOUT = ${ conf.EDITOR_AUTOCOMPLETE_TIMEOUT.get() };

  window.CACHEABLE_TTL = {
    default: ${ conf.CUSTOM.CACHEABLE_TTL.get() },
    optimizer: ${ OPTIMIZER.CACHEABLE_TTL.get() }
  };

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

  window.HAS_WORKLOAD_ANALYTICS = '${ has_workload_analytics() }' === 'True';

  window.HUE_CONTAINER = '${ IS_EMBEDDED.get() }' === 'True' ? '.hue-embedded-container' : 'body';

  window.IS_EMBEDDED = '${ IS_EMBEDDED.get() }' === 'True';

  window.HUE_I18n = {
    autocomplete: {
      category: {
        all: '${ _('All') }',
        column: '${ _('Columns') }',
        cte: '${ _('CTEs') }',
        database: '${ _('Databases') }',
        field: '${ _('Field') }',
        'function': '${ _('Functions') }',
        identifier: '${ _('Identifiers') }',
        keyword: '${ _('Keywords') }',
        popular: '${ _('Popular') }',
        sample: '${ _('Samples') }',
        table: '${ _('Tables') }',
        udf: '${ _('UDFs') }',
        option: '${ _('Options') }',
        variable: '${ _('Variables') }'
      },
      meta: {
        aggregateFunction: '${ _('aggregate') }',
        alias: '${ _('alias') }',
        commonTableExpression: '${ _('cte') }',
        database: '${ _('database') }',
        filter: '${ _('filter') }',
        groupBy: '${ _('group by') }',
        join: '${ _('join') }',
        joinCondition: '${ _('condition') }',
        keyword: '${ _('keyword') }',
        orderBy: '${ _('order by') }',
        table: '${ _('table') }',
        sample: '${ _('sample') }',
        variable: '${ _('variable') }',
        view: '${ _('view') }',
        virtual: '${ _('virtual') }'
      }
    },
    copyToClipboard: {
      error: "${ _('Error while copying results.') }",
      success: "${ _('result(s) copied to the clipboard') }",
    },
    documentType: {
      'all': '${_('All')}',
      'directory': '${ _('Directory') }',
      'link-pigscript': '${_('Pig Design')}',
      'link-workflow': '${_('Job Design')}',
      'notebook': '${_('Notebook')}',
      'oozie-bundle2': '${_('Oozie Bundle')}',
      'oozie-coordinator2': IS_HUE_4 ? '${_('Oozie Schedule')}' : '${_('Oozie Coordinator')}',
      'oozie-workflow2': '${_('Oozie Workflow')}',
      'query-hive': '${_('Hive Query')}',
      'query-impala': '${_('Impala Query')}',
      'search-dashboard': '${_('Search Dashboard')}',
      'query-mapreduce': '${_('MapReduce Job')}',
      'query-sqoop1': '${_('Import Job')}',
      'query-spark2': '${_('Spark Job')}',
      'query-java': '${_('Java Job')}',
      'query-pig': '${_('Pig Script')}',
      'query-shell': '${_('Shell Script')}',
      'query-distcp': '${_('DistCp Job')}'
    },
    dropzone: {
      cancelUpload: '${ _('Cancel upload') }',
      uploadCanceled: '${ _('The upload has been canceled') }',
      uploadSucceeded: '${ _('uploaded successfully') }'
    },
    jHueHdfsTree: {
      GO_TO_COLUMN: '${_('Go to column:')}',
      PLACEHOLDER: '${_('column name...')}',
      LOCK: '${_('Lock this row')}',
      UNLOCK: '${_('Unlock this row')}',
      ROW_DETAILS: '${_('Show row details')}'
    },
    jHueFileChooser: {
      BACK: '${_('Back')}',
      SELECT_FOLDER: '${_('Select this folder')}',
      CREATE_FOLDER: '${_('Create folder')}',
      FOLDER_NAME: '${_('Folder name')}',
      CANCEL: '${_('Cancel')}',
      FILE_NOT_FOUND: '${_('The file has not been found')}',
      UPLOAD_FILE: '${_('Upload a file')}',
      FAILED: '${_('Failed')}'
    },
    jHueTableExtender: {
      GO_TO_COLUMN: '${_('Go to column:')}',
      PLACEHOLDER: '${_('column name...')}',
      LOCK: '${_('Lock this row')}',
      UNLOCK: '${_('Unlock this row')}',
      ROW_DETAILS: '${_('Show row details')}'
    },
    metastore: {
      errorRefreshingTableStats: '${_('An error occurred refreshing the table stats. Please try again.')}'
    },
    selectize: {
      choose: "${ _('Choose...') }",
      editTags: "${ _('Edit tags') }"
    },
    syntaxChecker: {
      didYouMean: '${_('Did you mean')}',
      expectedStatementEnd: '${_('Expected end of statement')}',
      suppressError: '${_('Ignore this type of error')}',
      couldNotFind: '${_('Could not find')}'
    },
    queryBuilder: {
      insertValueHere: "${ _('Insert value here') }",
      queryRequire: "${ _('Query requires a select or aggregate.') }"
    },
    chart: {
      noData: "${ _('No Data Available.') }",
      missingLegend: "${ _('Missing legend configuration.') }",
      missingValue: "${ _('Missing value configuration.') }",
      missingX: "${ _('Missing x axis configuration.') }",
      missingY: "${ _('Missing y axis configuration.') }",
      missingLatitude: "${ _('Missing latitude configuration.') }",
      missingLongitude: "${ _('Missing longitude configuration.') }",
      missingLabel: "${ _('Missing label configuration.') }",
      missingRegion: "${ _('Missing region configuration.') }",
    }
  };

  window.HUE_VERSION = '${ hue_version() }';

  %if hasattr(ENABLE_NEW_INDEXER, 'get') and ENABLE_NEW_INDEXER.get():
    window.IS_NEW_INDEXER_ENABLED = true;
  %else:
    window.IS_NEW_INDEXER_ENABLED = false;
  %endif

  window.IS_S3_ENABLED = '${ is_s3_enabled }' === 'True';

  var docTypes = [];
  Object.keys(window.HUE_I18n.documentType).forEach(function (key) {
    if (key !== 'all') {
      docTypes.push({ type: key, label: window.HUE_I18n.documentType[key] });
    }
  })
  docTypes.sort(function (a, b) { return a.label.localeCompare(b.label); });
  docTypes.unshift({ type: 'all', label: window.HUE_I18n.documentType['all'] });
  window.DOCUMENT_TYPES = docTypes;

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