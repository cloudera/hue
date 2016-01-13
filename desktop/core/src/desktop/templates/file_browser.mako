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
from desktop import conf
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%def name="fileBrowser()">
  <style>

  </style>

  <script type="text/html" id="file-browser-template">
    Hello
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        define('fileBrowser', [
          'knockout'
        ], factory);
      } else {
        factory(ko);
      }
    }(function (ko) {

      /**
       * @param {Object} options
       * @constructor
       */
      function FileBrowser (options) {
        var self = this;
      }

      ko.components.register('file-browser', {
        viewModel: FileBrowser,
        template: { element: 'file-browser-template' }
      });
    }));
  </script>
</%def>