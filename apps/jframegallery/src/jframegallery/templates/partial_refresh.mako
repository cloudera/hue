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
<%
count = int(get_var('count', 0))
%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
  <head>
    <title>Partial Refresh</title>
    <meta http-equiv="refresh" content="2;/jframegallery/partial_refresh.mako?sleep=1&count=${count + 1}" />
  </head>
  <body>
    <div class="jframe_padded partial_refresh">
      <h2 data-partial-id="0">The current time: ${datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</h2>
      <a data-filters="ArtButton" data-partial-id="1">current time: ${datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</a>
      <br/>
      <textarea type="text">you can change this</textarea>
      <p>you can interact with the input above while the blocks with the time stamps update. Note that the button is rendered each time and your input changes aren't.</p>
      <hr/>
      <p>
        The table below will continue to grow until there are 10 rows; the time in each row will update with each refresh.
      </p>
      <table class="HtmlTable">
        <thead>
          <tr>
            <th>count</th>
            <th>current time</th>
          </tr>
        </thead>
        <tbody data-partial-container-id="partials-tbody">
          <% index = 0 %>
          % while index < count and index < 10:
            <tr data-partial-line-id="tr-${index}">
              <td data-partial-id="index-${index}">${index}</td>
              <td data-partial-id="time-${index}">${datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td>
            </tr>
            <% index = index + 1 %>
          % endwhile
        </tbody>
      </table>
      <hr/>
      <p>
        The table below will shrink from 10 rows down to zero; the time in each row will update on each refresh.
      </p>
      <table class="HtmlTable">
        <thead>
          <tr>
            <th>count</th>
            <th>current time</th>
          </tr>
        </thead>
        <tbody data-partial-container-id="partials-tbody-down">
          <%
            count = 10 - count
            index = 0 %>
          % while index < count:
            <tr data-partial-line-id="tr-down-${index}">
              <td data-partial-id="index-down-${index}">${index}</td>
              <td data-partial-id="time-down-${index}">${datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td>
            </tr>
            <% index = index + 1 %>
          % endwhile
        </tbody>
      </table>
    </div>
  </body>
</html>
