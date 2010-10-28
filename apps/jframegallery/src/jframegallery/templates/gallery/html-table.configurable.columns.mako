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

<%
  data = [
    {"id":56,"timezone":"Europe/Amsterdam","name":"Amsterdam","geo/lat":52.3789,"geo/long":4.90067},
    {"id":46,"timezone":"America/New_York","name":"Atlanta","geo/lat":33.7525,"geo/long":-84.3888},
    {"id":42,"timezone":"America/Chicago","name":"Austin","geo/lat":30.2669,"geo/long":-97.7428},
    {"id":63,"timezone":"America/New_York","name":"Baltimore","geo/lat":39.294255,"geo/long":-76.614275},
    {"id":24,"timezone":"America/New_York","name":"Boston","geo/lat":42.3583,"geo/long":-71.0603},
    {"id":32,"timezone":"America/Chicago","name":"Chicago","geo/lat":41.8858,"geo/long":-87.6181},
    {"id":64,"timezone":"America/New_York","name":"Cleveland","geo/lat":41.499819,"geo/long":-81.693716},
    {"id":43,"timezone":"America/Chicago","name":"Dallas / Fort Worth","geo/lat":32.7887,"geo/long":-96.7676},
    {"id":25,"timezone":"America/Denver","name":"Denver","geo/lat":39.734,"geo/long":-105.026},
    {"id":47,"timezone":"America/New_York","name":"Detroit","geo/lat":42.3333,"geo/long":-83.0484},
    {"id":48,"timezone":"America/Chicago","name":"Houston","geo/lat":29.7594,"geo/long":-95.3594},
    {"id":66,"timezone":"America/New_York","name":"Indianapolis","geo/lat":39.767016,"geo/long":-86.156255},
    {"id":65,"timezone":"America/Chicago","name":"Kansas City","geo/lat":39.090431,"geo/long":-94.583644},
    {"id":49,"timezone":"America/Los_Angeles","name":"Las Vegas","geo/lat":36.1721,"geo/long":-115.122},
    {"id":61,"timezone":"Europe/London","name":"London","geo/lat":51.50714,"geo/long":-0.126171},
    {"id":34,"timezone":"America/Los_Angeles","name":"Los Angeles","geo/lat":34.0443,"geo/long":-118.251},
    {"id":39,"timezone":"America/New_York","name":"Miami","geo/lat":25.7323,"geo/long":-80.2436},
    {"id":67,"timezone":"America/Chicago","name":"Milwaukee","geo/lat":43.038902,"geo/long":-87.906474},
    {"id":51,"timezone":"America/Chicago","name":"Minneapolis / St. Paul","geo/lat":44.9609,"geo/long":-93.2642},
    {"id":70,"timezone":"America/New_York","name":"Montreal","geo/lat":45.545447,"geo/long":-73.639076},
    {"id":52,"timezone":"America/Chicago","name":"New Orleans","geo/lat":29.9544,"geo/long":-90.075},
    {"id":22,"timezone":"America/New_York","name":"New York City","geo/lat":40.7255,"geo/long":-73.9983},
    {"id":72,"timezone":"America/Chicago","name":"Omaha","geo/lat":41.254006,"geo/long":-95.999258},
    {"id":33,"timezone":"America/New_York","name":"Philadelphia","geo/lat":39.8694,"geo/long":-75.2731},
    {"id":53,"timezone":"America/Phoenix","name":"Phoenix","geo/lat":33.4483,"geo/long":-112.073},
    {"id":60,"timezone":"America/New_York","name":"Pittsburgh","geo/lat":40.4405,"geo/long":-79.9961},
    {"id":37,"timezone":"America/Los_Angeles","name":"Portland","geo/lat":45.527,"geo/long":-122.685},
    {"id":57,"timezone":"America/New_York","name":"Raleigh / Durham","geo/lat":35.7797,"geo/long":-78.6434},
    {"id":73,"timezone":"America/New_York","name":"Richmond","geo/lat":37.542979,"geo/long":-77.469092},
    {"id":71,"timezone":"America/Denver","name":"Salt Lake City","geo/lat":40.760779,"geo/long":-111.891047},
    {"id":68,"timezone":"America/Chicago","name":"San Antonio","geo/lat":29.424122,"geo/long":-98.493628},
    {"id":38,"timezone":"America/Los_Angeles","name":"San Diego","geo/lat":32.7153,"geo/long":-117.156},
    {"id":23,"timezone":"America/Los_Angeles","name":"San Francisco","geo/lat":37.7587,"geo/long":-122.433},
    {"id":41,"timezone":"America/Los_Angeles","name":"Seattle","geo/lat":47.6036,"geo/long":-122.326},
    {"id":62,"timezone":"America/Chicago","name":"St. Louis","geo/lat":38.627491,"geo/long":-90.198417},
    {"id":69,"timezone":"America/New_York","name":"Toronto","geo/lat":43.670233,"geo/long":-79.386755},
    {"id":59,"timezone":"America/Vancouver","name":"Vancouver","geo/lat":49.259515,"geo/long":-123.103867},
    {"id":31,"timezone":"America/New_York","name":"Washington, DC","geo/lat":38.8964,"geo/long":-77.0447}
  ]
  columns = ['id', 'timezone', 'name', 'geo/lat', 'geo/long']
  active_columns = columns[:]
  if get_var('show_columns') is not None:
    active_columns = []
    for col in get_list('show_columns'):
        active_columns.append(columns[int(col)])
%>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
  <head>
    <title>Configurable Columns</title>
  </head>
  <body data-filters="CollapsingElements">
    <form action="${request_path}" method="GET" class="ccs-hidden collapsible ccs-table_config">
      <ul>
        % for i, option in enumerate(columns):
          <%
            checked = ""
            if option in active_columns:
              checked = 'checked="checked"'
          %>
          <li><label><input type="checkbox" name="show_columns" value="${i}" ${checked}/> ${option}</label></li>
        % endfor
      </ul>
      <a class="ccs-checkAll" data-filters="ArtButton" data-check-group=".ccs-table_config input">checkAll</a>
      <a class="ccs-checkNone" data-filters="ArtButton" data-check-group=".ccs-table_config input">checkNone</a>
      <input type="submit" value="Apply" data-filters="ArtButton"/>
    </form>
    <table data-filters="HtmlTable">
      <thead>
        <tr>
          % for i, col in enumerate(active_columns):
            % if i == 0:
              <th>
                <a class="collapser ccs-table_config_link ccs-left"></a>
                ${col}
              </th>
            % else:
              <th>${col}</th>
            % endif
          % endfor
        </tr>
      </thead>
      <tbody>
        % for d in data:
          <tr>
          % for name in active_columns:
              <td>
                ${d.get(name)}
              </td>
          % endfor
          </tr>
        % endfor
      </tbody>
    </table>
    
  </body>
</head>