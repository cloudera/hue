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

<%namespace name="require" file="/require.mako" />

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <title>Jasmine Spec Runner</title>

    <link rel="shortcut icon" type="image/png" href="${ static('desktop/ext/js/jasmine-2.3.4/jasmine_favicon.png') }">
    <link rel="stylesheet" href="${ static('desktop/ext/js/jasmine-2.3.4/jasmine.css') }">

    <script type="text/javascript" src="${ static('desktop/ext/js/jquery/jquery-2.1.1.min.js') }"></script>
    <script type="text/javascript" src="${ static('desktop/js/jquery.migration.js') }"></script>
    <script type="text/javascript" src="${ static('desktop/ext/js/jquery/plugins/jquery.total-storage.min.js') }"></script>

    ${ require.config() }

    <script type="text/javascript" charset="utf-8">
      // Adds the jasmine dependencies to the existing require config.
      require.config({
        urlArgs: "random=" + Math.random(),
        baseUrl: "${ static('') }",
        paths: {
          'jasmine': 'desktop/ext/js/jasmine-2.3.4/jasmine',
          'jasmine-html': 'desktop/ext/js/jasmine-2.3.4/jasmine-html',
          'jasmine-boot': 'desktop/ext/js/jasmine-2.3.4/boot'
        },
        shim: {
          'jasmine-html': {
            deps : ['jasmine']
          },
          'jasmine-boot': {
            deps : ['jasmine', 'jasmine-html']
          }
        }
      })
    </script>

    <%block name="specs"/>
</head>

<body>
    <%block name="fixtures"/>
</body>
</html>
