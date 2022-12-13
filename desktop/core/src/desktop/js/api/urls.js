// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

export const AUTOCOMPLETE_API_PREFIX = '/api/editor/autocomplete/';
export const BANNERS_API = '/api/banners/';
export const SAMPLE_API_PREFIX = '/notebook/api/sample/';
export const EXECUTE_API_PREFIX = '/api/editor/execute/'; // Dups with api.ts
export const DOCUMENTS_API = '/desktop/api2/doc/';
export const DOCUMENTS_SEARCH_API = '/desktop/api2/docs/';
export const GET_HUE_CONFIG_API = '/desktop/api2/get_hue_config';
export const FETCH_CONFIG_API = '/api/get_config/';
export const HDFS_API_PREFIX = '/filebrowser/view=' + encodeURIComponent('/');
export const ADLS_API_PREFIX = '/filebrowser/view=' + encodeURIComponent('adl:/');
export const ABFS_API_PREFIX = '/filebrowser/view=' + encodeURIComponent('ABFS://');
export const GIT_API_PREFIX = '/desktop/api/vcs/contents/';
export const S3_API_PREFIX = '/filebrowser/view=' + encodeURIComponent('s3a://');
export const IMPALA_INVALIDATE_API = '/impala/api/invalidate';
export const CONFIG_SAVE_API = '/desktop/api/configurations/save/';
export const CONFIG_APPS_API = '/desktop/api/configurations';
export const SOLR_COLLECTIONS_API = '/indexer/api/indexes/list/';
export const SOLR_FIELDS_API = '/indexer/api/index/list/';
export const DASHBOARD_TERMS_API = '/dashboard/get_terms';
export const DASHBOARD_STATS_API = '/dashboard/get_stats';
export const FORMAT_SQL_API = '/notebook/api/format';
export const GIST_API = '/desktop/api2/gist/';
export const GET_SLACK_CHANNELS = '/desktop/slack/api/channels/get';
export const SEND_SLACK_MESSAGE = '/desktop/slack/api/message/send';
export const TOPO_URL = '/desktop/topo/';

export const SEARCH_API = '/desktop/api/search/entities';
export const INTERACTIVE_SEARCH_API = '/api/metadata/search/entities_interactive';

export const CREATE_SESSION_API = '/api/editor/create_session'; // Note: dup by api.ts
export const CLOSE_SESSION_API = '/api/editor/close_session'; // Note: dup by api.ts
export const FETCH_RESULT_SIZE_API = '/notebook/api/fetch_result_size';
export const FETCH_RESULT_DATA_API = '/notebook/api/fetch_result_data';
export const GET_LOGS_API = '/api/editor/get_logs';
export const CANCEL_STATEMENT_API = '/notebook/api/cancel_statement';
export const CLOSE_STATEMENT_API = '/notebook/api/close_statement';
export const CHECK_STATUS_API = '/api/editor/check_status';

export const HBASE_API_PREFIX = '/hbase/api/';
export const SAVE_TO_FILE_API = '/filebrowser/save';

export const NAV_API = {
  ADD_TAGS: '/metadata/api/catalog/add_tags',
  DELETE_TAGS: '/metadata/api/catalog/delete_tags',
  FIND_ENTITY: '/metadata/api/catalog/find_entity',
  LIST_TAGS: '/metadata/api/catalog/list_tags',
  UPDATE_PROPERTIES: '/metadata/api/catalog/update_properties'
};
