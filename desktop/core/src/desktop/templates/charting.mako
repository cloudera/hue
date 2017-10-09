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
%>

<%def name="import_charts()">
  <link rel="stylesheet" href="${ static('desktop/ext/css/hue-charts.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.markercluster.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.zoombox.css') }">

  <script src="${ static('desktop/js/hue.geo.js') }"></script>

  <script src="${ static('desktop/ext/js/leaflet/leaflet.js') }"></script>
  <script src="${ static('desktop/ext/js/leaflet/leaflet.markercluster.js') }"></script>
  <script src="${ static('desktop/ext/js/leaflet/leaflet.zoombox.js') }"></script>
  <script src="${ static('desktop/ext/js/leaflet/leaflet.heat.js') }"></script>

  %if conf.USE_NEW_CHARTS.get():
  <script src="${ static('desktop/ext/js/plotly-latest.min.js') }"></script>
  <script src="${ static('desktop/js/ko.charts.plotly.js') }"></script>
  <script src="${ static('desktop/js/ko.charts.leaflet.js') }"></script>
  %else:
  <link rel="stylesheet" href="${ static('desktop/ext/css/nv.d3.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/css/nv.d3.css') }">

  <script src="${ static('desktop/ext/js/d3.v3.js') }"></script>
  <script src="${ static('desktop/ext/js/d3.v4.js') }"></script>
  <script src="${ static('desktop/js/nv.d3.js') }"></script>
  <script src="${ static('desktop/ext/js/topojson.v1.min.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/world.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/usa.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/chn.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/bra.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/can.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/ind.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/gbr.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/ita.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/fra.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/deu.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/jpn.topo.js') }"></script>
  <script src="${ static('desktop/ext/js/topo/aus.topo.js') }"></script>

  <script src="${ static('desktop/js/nv.d3.datamaps.js') }"></script>
  <script src="${ static('desktop/js/nv.d3.legend.js') }"></script>
  <script src="${ static('desktop/js/nv.d3.multiBarWithBrushChart.js') }"></script>
  <script src="${ static('desktop/js/nv.d3.lineWithBrushChart.js') }"></script>
  <script src="${ static('desktop/js/nv.d3.growingDiscreteBar.js') }"></script>
  <script src="${ static('desktop/js/nv.d3.growingDiscreteBarChart.js') }"></script>
  <script src="${ static('desktop/js/nv.d3.growingMultiBar.js') }"></script>
  <script src="${ static('desktop/js/nv.d3.growingMultiBarChart.js') }"></script>
  <script src="${ static('desktop/js/nv.d3.growingPie.js') }"></script>
  <script src="${ static('desktop/js/nv.d3.growingPieChart.js') }"></script>
  <script src="${ static('desktop/js/ko.charts.js') }"></script>
  <script src="${ static('desktop/js/ko.charts.leaflet.js') }"></script>
  %endif

</%def>
