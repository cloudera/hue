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
  from desktop.models import hue_version
%>

<html>
<body></body>
<script type="text/javascript">
  (function () {
    if (window.Worker) {
      var baseUrl = window.location.href.substring(0, window.location.href.indexOf('/notebook/workers_embedded'));
      // It can take a while before the worker is active
      var whenWorkerIsReady = function (worker, message) {
        if (!worker.isReady) {
          window.clearTimeout(worker.pingTimeout);
          worker.postMessage({ ping: true });
          worker.pingTimeout = window.setTimeout(function () {
            whenWorkerIsReady(worker, message);
          }, 500);
        } else {
          worker.postMessage(message);
        }
      };

      // For syntax checking
      var aceSqlSyntaxWorker = new Worker(baseUrl + '/desktop/workers/aceSqlSyntaxWorker.js?v=${ hue_version() }');
      aceSqlSyntaxWorker.onmessage = function (e) {
        if (e.data.ping) {
          aceSqlSyntaxWorker.isReady = true;
        } else {
          window.top.postMessage({ syntaxWorkerResponse: e.data }, '*');
        }
      };

      // For location marking
      var aceSqlLocationWorker = new Worker(baseUrl + '/desktop/workers/aceSqlLocationWorker.js?v=${ hue_version() }');
      aceSqlLocationWorker.onmessage = function (e) {
        if (e.data.ping) {
          aceSqlLocationWorker.isReady = true;
        } else {
          window.top.postMessage({ locationWorkerResponse: e.data }, '*');
        }
      };

      window.addEventListener("message", function (event) {
        if (event.data.locationWorkerRequest) {
          whenWorkerIsReady(aceSqlLocationWorker, event.data.locationWorkerRequest);
        }
        if (event.data.syntaxWorkerRequest) {
          whenWorkerIsReady(aceSqlSyntaxWorker, event.data.syntaxWorkerRequest);
        }
      }, false);
    }
  })();
</script>
</html>