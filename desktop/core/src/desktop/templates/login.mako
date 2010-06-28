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

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">

##
## This is used by the non-jframe login
##

<html><head><title>Hue Login</title></head>
<body>
  <form method="POST" action="${action}">
    ${form.as_ul() | n}
    <input type="submit" value="login" />
    <input type="hidden" name="next" value="${next}" />
  </form>
</body>
</html>
