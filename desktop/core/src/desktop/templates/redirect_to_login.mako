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

<!DOCTYPE html>
<html>
<head>
  <title>Redirecting to login...</title>
</head>
<body>
  <script>
    var browserUrl = window.location.pathname + window.location.search + window.location.hash;
    window.location.href = '${login_url}?${redirect_field_name}=' + encodeURIComponent(browserUrl);
  </script>
  <noscript>
    <p>Please <a href="${login_url}">click here to login</a>.</p>
  </noscript>
</body>
</html>
