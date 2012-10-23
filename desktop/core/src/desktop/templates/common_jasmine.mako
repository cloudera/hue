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

    <link rel="stylesheet" type="text/css" href="/static/ext/css/jasmine.css">
    <script type="text/javascript" src="/static/ext/js/jasmine/jasmine-1.2.0.js"></script>
    <script type="text/javascript" src="/static/ext/js/jasmine/jasmine-html-1.2.0.js"></script>
    <script type="text/javascript" src="/static/ext/js/jquery/jquery-1.8.1.min.js"></script>
    <script type="text/javascript" src="/static/ext/js/jasmine/jasmine-jquery-1.3.1.js"></script>
    <script type="text/javascript" src="/static/ext/js/knockout-2.1.0.js"></script>

    <%block name="specs"/>

    <script type="text/javascript">
        (function() {
            var jasmineEnv = jasmine.getEnv();
            jasmineEnv.updateInterval = 1000;

            var htmlReporter = new jasmine.HtmlReporter();

            jasmineEnv.addReporter(htmlReporter);

            jasmineEnv.specFilter = function(spec) {
                return htmlReporter.specFilter(spec);
            };

            var currentWindowOnload = window.onload;

            window.onload = function() {
                if (currentWindowOnload) {
                    currentWindowOnload();
                }
                execJasmine();
            };

            function execJasmine() {
                jasmineEnv.execute();
            }

        })();
    </script>

</head>

<body>
    <%block name="fixtures"/>
</body>
</html>
