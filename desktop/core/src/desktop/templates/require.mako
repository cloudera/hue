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
from desktop.conf import DJANGO_DEBUG_MODE
from django.conf import settings
DEBUG = DJANGO_DEBUG_MODE.get()
%>


<%def name="config()">
  <script src="${ static('desktop/ext/js/require.js') }"></script>
  <script>
    define('jquery', [], function() {
      return jQuery;
    });
    require.config({
      %if DEBUG:
      urlArgs: "bust=" + (new Date()).getTime(),
      %else:
      urlArgs: "version=${settings.HUE_DESKTOP_VERSION}",
      %endif
      baseUrl: "${ static('') }",
      paths: {
        "jquery.ui.sortable": "desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min",
        "knockout": "desktop/ext/js/knockout.min",
        "ko.charts" : "desktop/js/ko.charts",
        "knockout-mapping" : "desktop/ext/js/knockout-mapping.min",
        "knockout-sortable" : "desktop/ext/js/knockout-sortable.min",
        "ko.editable" : "desktop/js/ko.editable",
        "ko.hue-bindings" : "desktop/js/ko.hue-bindings"
      },
      shim: {
        "knockout": { exports: "ko" },
        "knockout-mapping": { deps: ["knockout"] },
        "knockout-sortable": { deps: ["knockout", "jquery", "jquery.ui.sortable"] },
        "ko.editable": { deps: ["knockout"] },
        "ace.extended": { deps: ["ace"] },
        "ace.ext-language-tools": { deps: ["ace"] }
      },
      deps: ["knockout", "knockout-mapping"],
      callback: function(ko, mapping) {
        ko.mapping = mapping;
        window.hueDebug = {
          ko: ko,
          viewModel: function () {
            return ko.dataFor(document.body);
          }
        }
      }
    });
  </script>
</%def>