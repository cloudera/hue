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
from datetime import datetime
%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
  <head>
    <title>Partial Refresh</title>
    <meta http-equiv="refresh" content="2;/jframegallery/partial_refresh.mako?sleep=1" />
  </head>
  <body>
    <div class="jframe_padded partial_refresh">
      <h2 data-partial-id="0">The current time: ${datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</h2>
      <a data-filters="ArtButton" data-partial-id="1">current time: ${datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</a>
      <br/>
      <textarea type="text">you can change this</textarea>
      <p>you can interact with the input above while the blocks with the time stamps update. Note that the button is rendered each time and your input changes aren't.</p>
    </div>
  </body>
</html>
