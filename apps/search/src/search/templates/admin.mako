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
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="macros" file="macros.mako" />
<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(_('Search'), "search", user) | n,unicode }

<link rel="stylesheet" href="/search/static/css/admin.css">

<div class="container-fluid">
  <h1>${_('Search Admin - Cores')}</h1>
  <%actionbar:render>
    <%def name="search()">
      <input type="text" placeholder="${_('Filter cores by name...')}" class="input-xxlarge search-query" id="filterInput">
    </%def>
  </%actionbar:render>
  <div class="row-fluid">
    <div class="span12">
      <ul id="cores">
      % for core in hue_cores:
        <li style="cursor: move" data-core="${ core.name }">
          <a href="${ core.get_absolute_url() }" class="pull-right" style="margin-top: 10px;margin-right: 10px"><i class="icon-edit"></i> ${_('Edit')}</a>
          <h4><i class="icon-list"></i> ${ core.name }</h4>
        </li>
      % endfor
      </ul>
    </div>
  </div>
</div>

<style type="text/css">
  #cores {
    list-style-type: none;
    margin: 0;
    padding: 0;
    width: 100%;
  }

  #cores li {
    margin-bottom: 10px;
    padding: 10px;
    border: 1px solid #E3E3E3;
    height: 40px;
  }

  .placeholder {
    height: 40px;
    background-color: #F5F5F5;
    border: 1px solid #E3E3E3;
  }
</style>

<script src="/static/ext/js/jquery/plugins/jquery-ui-draggable-droppable-sortable-1.8.23.min.js"></script>

<script type="text/javascript">
  $(document).ready(function () {
    var orderedCores;
    serializeList();
    $("#cores").sortable({
      placeholder: "placeholder",
      update: function (event, ui) {
        serializeList();
        ##TODO: serialize via ajax the order of cores
        ## the array is: orderedCores
        ## console.log(orderedCores)
      }
    });
    $("#cores").disableSelection();

    function serializeList() {
      orderedCores = [];
      $("#cores li").each(function () {
        orderedCores.push($(this).data("core"));
      });
    }

    var filter = -1;
    $("#filterInput").on("keyup", function () {
      clearTimeout(filter);
      filter = window.setTimeout(function () {
        $("#cores li").removeClass("hide");
        $("#cores li").each(function () {
          if ($(this).data("core").toLowerCase().indexOf($("#filterInput").val().toLowerCase()) == -1) {
            $(this).addClass("hide");
          }
        });
      }, 300);
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
