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
  from webpack_loader import utils
%>

WorkerGlobalScope.KNOX_BASE_PATH_HUE = '/KNOX_BASE_PATH_HUE';
WorkerGlobalScope.HUE_BASE_URL = WorkerGlobalScope.KNOX_BASE_PATH_HUE.indexOf('KNOX_BASE_PATH_HUE') < 0 ? WorkerGlobalScope.KNOX_BASE_PATH_HUE : '';

% for js_file in utils.get_files('sqlLocationWebWorker', config='WORKERS'):
  importScripts('${ js_file.get('url') }');
% endfor

(function () {
  this.onmessage = WorkerGlobalScope.onLocationMessage
})();
