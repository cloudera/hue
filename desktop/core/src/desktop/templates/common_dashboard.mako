## -*- coding: utf-8 -*-
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


#
# Include this in order to use the functions:
# <%namespace name="dashboard" file="common_dashboard.mako" />
#

<%!
  from django.utils.translation import ugettext as _
%>


<%def name="import_bindings()">
  <link rel="stylesheet" href="/static/css/freshereditor.css">
  <link rel="stylesheet" href="/static/ext/css/codemirror.css">
  <link rel="stylesheet" href="/static/ext/css/bootstrap-editable.css">
  <link rel="stylesheet" href="/static/ext/css/bootstrap-datepicker.min.css">
  <link rel="stylesheet" href="/static/ext/css/bootstrap-timepicker.min.css">
  <link rel="stylesheet" href="/static/css/bootstrap-spinedit.css">
  <link rel="stylesheet" href="/static/css/bootstrap-slider.css">

  <script src="/static/ext/js/bootstrap-datepicker.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/bootstrap-timepicker.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/bootstrap-spinedit.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/bootstrap-slider.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/freshereditor.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/codemirror-3.11.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/codemirror-xml.js" type="text/javascript" charset="utf-8"></script>

  <script src="/static/ext/js/less-1.7.0.min.js" type="text/javascript" charset="utf-8"></script>


  <script type="text/javascript">
    KO_DATERANGEPICKER_LABELS = {
      START: "${_('Start')}",
      END: "${_('End')}",
      INTERVAL: "${_('Interval')}",
      CUSTOM_FORMAT: "${_('Custom Format')}",
      DATE_PICKERS: "${_('Date Pickers')}"
    };
  </script>
  <script src="/static/js/ko.hue-bindings.js" type="text/javascript" charset="utf-8"></script>

</%def>


<%def name="import_charts()">
  <link rel="stylesheet" href="/static/ext/css/leaflet.css">
  <link rel="stylesheet" href="/static/ext/css/nv.d3.min.css">
  <link rel="stylesheet" href="/static/css/nv.d3.css">

  <script src="/static/js/hue.geo.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/hue.colors.js" type="text/javascript" charset="utf-8"></script>

  <script src="/static/ext/js/leaflet/leaflet.js" type="text/javascript" charset="utf-8"></script>

  <script src="/static/ext/js/d3.v3.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/nv.d3.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/topojson.v1.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/topo/world.topo.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/topo/usa.topo.js" type="text/javascript" charset="utf-8"></script>

  <script src="/static/js/nv.d3.datamaps.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.legend.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.multiBarWithBrushChart.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.lineWithBrushChart.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingDiscreteBar.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingDiscreteBarChart.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingMultiBar.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingMultiBarChart.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingPie.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingPieChart.js" type="text/javascript" charset="utf-8"></script>

  <script src="/static/js/ko.charts.js" type="text/javascript" charset="utf-8"></script>

</%def>


