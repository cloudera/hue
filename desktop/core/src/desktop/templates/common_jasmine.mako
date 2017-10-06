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

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>Jasmine Spec Runner</title>

  <link rel="shortcut icon" type="image/png" href="${ static('desktop/ext/js/jasmine-2.3.4/jasmine_favicon.png') }">
  <link rel="stylesheet" href="${ static('desktop/ext/js/jasmine-2.3.4/jasmine.css') }">

  <script type="text/javascript" src="${ static('desktop/ext/js/jquery/jquery-2.2.4.min.js') }"></script>
  <script type="text/javascript" src="${ static('desktop/js/jquery.migration.js') }"></script>
  <script type="text/javascript" src="${ static('desktop/js/hue.utils.js') }"></script>
  <script type="text/javascript" src="${ static('desktop/ext/js/jquery/plugins/jquery.total-storage.min.js') }"></script>
  <script type="text/javascript" src="${ static('desktop/js/ace/ace.js') }"></script>
  <script>
    ace.config.set("basePath", "/static/desktop/js/ace");
  </script>

  <script type="text/javascript" src="${ static('desktop/js/ace/ext-language_tools.js') }"></script>
  <script type="text/javascript" src="${ static('desktop/js/ace.extended.js') }"></script>
  <script type="text/javascript" src="${ static('desktop/ext/js/jasmine-2.3.4/jasmine') }"></script>
  <script type="text/javascript" src="${ static('desktop/ext/js/jasmine-2.3.4/jasmine-html') }"></script>
  <script type="text/javascript" src="${ static('desktop/ext/js/jasmine-2.3.4/boot') }"></script>
  <script type="text/javascript" src="${ static('desktop/ext/js/jasmine-2.3.4/mock-ajax') }"></script>

  <%block name="specs"/>
</head>

<body>
  <%block name="fixtures"/>
</body>
</html>
