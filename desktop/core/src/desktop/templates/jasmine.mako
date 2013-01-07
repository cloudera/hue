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
##
##
## no spaces in this method please; we're declaring a CSS class, and ART uses this value for stuff, and it splits on spaces, and
## multiple spaces and line breaks cause issues

<%inherit file="common_jasmine.mako"/>

<%block name="specs">
  <link href="/static/css/hue2.css" rel="stylesheet">

  <script src="/static/ext/js/jquery/plugins/jquery.dataTables.1.8.2.min.js"></script>
  <script src="/static/ext/js/bootstrap.min.js"></script>

  <script src="/static/js/Source/jHue/jquery.selector.js"></script>
  <script src="static/jasmine/jHueSelectorSpec.js"></script>

  <script src="/static/js/Source/jHue/jquery.tableextender.js"></script>
  <script src="static/jasmine/jHueTableExtenderSpec.js"></script>

  <script src="/static/js/Source/jHue/jquery.tablescroller.js"></script>
  <script src="static/jasmine/jHueTableScrollerSpec.js"></script>
</%block>

