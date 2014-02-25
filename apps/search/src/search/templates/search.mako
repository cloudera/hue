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
from django.utils.dateparse import parse_datetime
from search.api import utf_quoter
import urllib
import math
import time
%>

<%namespace name="macros" file="macros.mako" />

${ commonheader(_('Search'), "search", user, "90px") | n,unicode }

<link rel="stylesheet" href="/search/static/css/search.css">
<link href="/static/ext/css/hue-filetypes.css" rel="stylesheet">
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/search.utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.selection.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.time.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.blueprint.js" type="text/javascript" charset="utf-8"></script>

<%
  if "q" not in solr_query:
    solr_query["q"] = ""
  else:
    solr_query["q"] = solr_query["q"].decode("utf8")
  if "fq" not in solr_query:
    solr_query["fq"] = ""
  if "rows" not in solr_query:
    solr_query["rows"] = ""
  if "start" not in solr_query:
    solr_query["start"] = ""
%>

<div class="search-bar">
  % if user.is_superuser:
    <div class="pull-right" style="margin-top: 6px; margin-right: 40px">
      <a class="change-settings" href="#"><i class="fa fa-edit"></i> ${ _('Customize this collection') }</a> &nbsp;&nbsp;
      <a href="${ url('search:admin_collections') }"><i class="fa fa-sitemap"></i> ${ _('Collection manager') }</a>
    </div>
  % endif
  <form class="form-search" style="margin: 0">
    <strong>${_("Search")}</strong>
    <div class="input-append">
      <div class="selectMask">
        % if len(hue_collections) > 1:
        <i class="fa fa-caret-down" style="float:right;margin-top: 8px; margin-left: 5px"></i>
        % endif
        <span class="current-collection"></span>
        <div id="collectionPopover" class="hide">
        <ul class="unstyled">
          % if user.is_superuser:
            % for collection in hue_collections:
              <li><a class="dropdown-collection" href="#" data-value="${ collection.id }" data-settings-url="${ collection.get_absolute_url() }">${ collection.label }</a></li>
            % endfor
          % else:
            % for collection in hue_collections:
              <li><a class="dropdown-collection" href="#" data-value="${ collection.id }">${ collection.label }</a></li>
            % endfor
          % endif
        </ul>
        </div>
      </div>

      ${ search_form | n,unicode }
      <button type="submit" id="search-btn" class="btn btn-inverse"><i class="fa fa-search"></i></button>

      % if response and 'response' in response and 'docs' in response['response'] and len(response['response']['docs']) > 0:
      <div class="btn-group download-btn-group" style="margin-left: 15px">
        <button type="button" id="download-btn" class="btn btn-inverse dropdown-toggle" data-toggle="dropdown"><i class="fa fa-download"></i></button>
        <ul class="dropdown-menu" role="menu">
          <li><a href="javascript:void(0)" id="download-xls"><i class="hfo hfo-file-xls"></i>&nbsp; ${ _('XLS') }</a></li>
          <li><a href="javascript:void(0)" id="download-csv"><i class="hfo hfo-file-csv">&nbsp; ${ _('CSV') }</i></a></li>
        </ul>
      </div>
      % endif
    </div>
  </form>
</div>

<div id="loader" class="row" style="text-align: center;margin-top: 20px">
  <!--[if lte IE 9]>
      <img src="/static/art/spinner-big.gif" />
  <![endif]-->
  <!--[if !IE]> -->
    <i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i>
  <!-- <![endif]-->
</div>

% if error:
<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">
      <div class="alert alert-error">
        % if error['title']:
        <h4>${ error['title'] }</h4><br/>
        % endif
        <span class="decodeError" data-message="${ error['message'] }"></span>
      </div>
    </div>
  </div>
</div>
% else:
<div class="container results">
  <div id="mainContent" class="row hide">
    % if response and 'response' in response and 'docs' in response['response'] and len(response['response']['docs']) > 0 and 'normalized_facets' in response:
      <% shown_facets = 0 %>
    <div class="span2 results">
      <ul class="facet-list">
        ## Force chart facets first
        % for fld in response['normalized_facets']:
          % if fld['type'] == 'chart':
            <%
            found_value = ""
            for fq in solr_query['fq'].split('|'):
              if fq and fq.split(':')[0] == fld['field']:
                found_value = fq[fq.find(":") + 1:]
                remove_list = solr_query['fq'].split('|')
                remove_list.remove(fq)
            %>
            %if found_value != "":
              <% shown_facets += 1 %>
              <li class="nav-header">${fld['label']}</li>
              <li><strong>${ found_value }</strong> <a href="?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${utf_quoter('|'.join(remove_list))}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}"><i class="fa fa-times"></i></a></li>
            %endif
          % endif
        % endfor
        % for fld in response['normalized_facets']:
          % if fld['type'] != 'chart':
            <% shown_facets += 1 %>
            % if fld['type'] == 'date':
              <li class="nav-header facetHeader dateFacetHeader">${fld['label']}</li>
            % else:
              <li class="nav-header facetHeader">${fld['label']}</li>
            % endif

            <%
            found_value = ""
            for fq in solr_query['fq'].split('|'):
              if fq and fq.split(':')[0] == fld['field']:
                found_value = fq[fq.find(":") + 1:]
                remove_list = solr_query['fq'].split('|')
                remove_list.remove(fq)
            %>
            % for group, count in macros.pairwise(fld['counts']):
              % if count > 0 and group != "" and found_value == "" and loop.index < 100:
                % if fld['type'] == 'field':
                  <li class="facetItem"><a href='?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${ utf_quoter(solr_query['fq']) }|${ fld['field'] }:"${utf_quoter(group)}"${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}'>${group}</a> <span class="counter">(${ count })</span></li>
                % endif
                % if fld['type'] == 'range':
                  <li class="facetItem"><a href='?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${ utf_quoter(solr_query['fq']) }|${ fld['field'] }:["${ group }" TO "${ str(int(group) + int(fld['gap']) - 1) }"]${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}'>${ group } - ${ str(int(group) + int(fld['gap']) - 1) }</a> <span class="counter">(${ count })</span></li>
                % endif
                % if fld['type'] == 'date':
                  <li class="facetItem dateFacetItem"><a href='?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${ utf_quoter(solr_query['fq']) }|${ fld['field'] }:[${ group } TO ${ group }${ utf_quoter(fld['gap']) }]${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}'><span class="dateFacet" data-format="${fld['format']}">${ group }<span class="dateFacetGap hide">${ fld['gap'] }</span></span></a> <span class="counter">(${ count })</span></li>
                % endif
              % endif
              % if found_value != "" and loop.index < 100:
                % if fld['type'] == 'field' and '"' + group + '"' == found_value:
                  <li class="facetItem"><strong>${ group }</strong> <a href="?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${utf_quoter('|'.join(remove_list))}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}"><i class="fa fa-times"></i></a></li>
                % endif
                % if fld['type'] == 'range' and '["' + group + '" TO "' + str(int(group) + int(fld['gap']) - 1) + '"]' == found_value:
                  <li class="facetItem"><strong>${ group } - ${ str(int(group) + int(fld['gap']) - 1) }</strong> <a href="?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${utf_quoter('|'.join(remove_list))}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}"><i class="fa fa-times"></i></a></li>
                % endif
                % if fld['type'] == 'date' and found_value.startswith('[' + group + ' TO'):
                  <li class="facetItem"><strong><span class="dateFacet" data-format="${fld['format']}">${ group }<span class="dateFacetGap hide">${ fld['gap'] }</span></span></strong> <a href="?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${utf_quoter('|'.join(remove_list))}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}"><i class="fa fa-times"></i></a></li>
                % endif
              % endif
            % endfor
          % endif
        % endfor
      </ul>
    </div>
    % endif

    % if response and 'response' in response and 'docs' in response['response'] and len(response['response']['docs']) > 0:
      % if response['normalized_facets'] and shown_facets > 0:
      <div class="span10 results">
      % else:
      <div class="span12 results">
      % endif
      <ul class="breadcrumb">
        <li class="pull-right">
          <div id="sortBy" style="display: inline" class="dropdown">
            Sort by <a data-toggle="dropdown" href="#"><strong></strong> <i class="fa fa-caret-down"></i></a>
            <ul class="dropdown-menu">
            </ul>
          </div>
        </li>
        <li class="active">
        <%
          end_record = int(solr_query["start"])+int(solr_query["rows"])
          if end_record > int(response['response']['numFound']):
            end_record = response['response']['numFound'];
        %>
          ${_('Page %s of %s. Showing %s results (%s seconds)') % (solr_query["current_page"], solr_query["total_pages"], response['response']['numFound'], float(solr_query["search_time"])/1000)}
        </li>
      </ul>

      % for fld in response['normalized_facets']:
        %if fld['type'] == 'chart':
          <%
            values = ""
            for group, count in macros.pairwise(fld['counts']):
              values += "['" + group + "'," + str(count) + "],"
          %>
          <div class="chartComponent" data-values="[${values[:-1]}]" data-label="${fld['label']}" data-field="${fld['field']}" data-gap="${'gap' in fld and fld['gap'] or ''}">
            <!--[if lte IE 9]>
              <img src="/static/art/spinner-big.gif" />
            <![endif]-->
            <!--[if !IE]> -->
              <i class="fa fa-spinner fa-spin" style="font-size: 24px; color: #DDD"></i>
            <!-- <![endif]-->
          </div>
        %endif
      % endfor

      <script src="/static/ext/js/mustache.js"></script>

      <div id="result-container"></div>

      <textarea id="mustacheTmpl" class="hide">${ hue_collection.result.get_template(with_highlighting=True) | n,unicode }</textarea>
      <script>

        <%
          docs = response['response']['docs']
          for doc in response['response']['docs']:
            # Beware, schema requires an 'id' field, silently do nothing
            if 'id' in doc and doc['id'] in response.get('highlighting', []):
              doc.update(response['highlighting'][doc['id']])
        %>

        var _mustacheTmpl = fixTemplateDotsAndFunctionNames($("#mustacheTmpl").text());
        $.each(${ json.dumps([result for result in docs]) | n,unicode }, function (index, item) {
          addTemplateFunctions(item);
          $("<div>").addClass("result-row").html(
            Mustache.render(_mustacheTmpl, item)
          ).appendTo($("#result-container"));
        });
      </script>

      <div class="pagination">
        <ul>
          <%
            pages_to_show = 5 # always use an odd number since we do it symmetrically

            beginning = 0
            previous = int(solr_query["start"]) - int(solr_query["rows"])
            next = int(solr_query["start"]) + int(solr_query["rows"])

            pages_after = (pages_to_show - 1) / 2
            pages_total = solr_query['total_pages']+1
            real_pages_after =  pages_total - solr_query["current_page"]
            symmetric_start = solr_query["current_page"] < pages_total - pages_after
            symmetric_end = solr_query["current_page"] > pages_after

            pagination_start = solr_query["current_page"] > (pages_to_show - 1)/2 and (symmetric_start and solr_query["current_page"] - (pages_to_show - 1)/2 or solr_query["current_page"] - pages_to_show + real_pages_after ) or 1
            pagination_end = solr_query["current_page"] < solr_query['total_pages']+1-(pages_to_show - 1)/2 and (symmetric_end and solr_query["current_page"] + (pages_to_show - 1)/2 + 1 or solr_query["current_page"] + (pages_to_show - solr_query["current_page"]) + 1) or solr_query['total_pages']+1
          %>
          % if int(solr_query["start"]) > 0:
            <li>
              <a title="${_('Previous Page')}" href="?collection=${ current_collection }&query=${solr_query["q"]}&fq=${utf_quoter(solr_query["fq"])}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}&rows=${solr_query["rows"]}&start=${previous}">${_('Previous Page')}</a>
            </li>
          % endif
          % for page in range(pagination_start, pagination_end):
            %if page > 0 and page < pages_total:
            <li
             %if solr_query["current_page"] == page:
               class="active"
             %endif
                >
              <a href="?collection=${ current_collection }&query=${solr_query["q"]}&fq=${utf_quoter(solr_query["fq"])}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}&rows=${solr_query["rows"]}&start=${(int(page)-1)*int(solr_query["rows"])}">${page}</a>
            </li>
            %endif
          % endfor
          % if end_record < int(response["response"]["numFound"]):
            <li>
              <a title="Next page" href="?collection=${ current_collection }&query=${solr_query["q"]}&fq=${utf_quoter(solr_query["fq"])}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}&rows=${solr_query["rows"]}&start=${next}">${_('Next Page')}</a>
            </li>
          % endif
        </ul>
      </div>
    </div>
    % else:
    <div class="span12">
      <h4>
        ${_('Your search')} - <strong>${solr_query["q"]}</strong> - ${_('did not match any documents.')}
      </h4>
      ${_('Suggestions:')}
      <ul>
        <li>${_('Make sure all words are spelled correctly.')}</li>
        <li>${_('Try different keywords.')}</li>
        <li>${_('Try more general keywords.')}</li>
        <li>${_('Try fewer keywords.')}</li>
      </ul>
    </div>
    % endif
  </div>
</div>

% endif

% if hue_collection:
  ${ hue_collection.result.get_extracode() | n,unicode }
% endif

<script>
  $(document).ready(function () {

    if ($(".errorlist").length > 0) {
      $(".errorlist li").each(function () {
        $(document).trigger("error", $(this).text());
      });
    }

    $(".decodeError").text($("<span>").html($(".decodeError").data("message")).text());

    $("#loader").hide();
    $("#mainContent").removeClass("hide");
    window.onbeforeunload = function (e) {
      $("#loader").show();
      $("#mainContent").addClass("hide");
    };

    var collectionProperties = ${ hue_collection.facets.data | n,unicode }.properties;
    $(".facetHeader").each(function(cnt, section){
      var _added = 0;
      var _showMore = false;
      var _lastSection = null;
      $(section).nextUntil(".facetHeader").each(function(cnt, item){
        if (cnt < collectionProperties.limit*1){ // it's a string, *1 -> number
          $(item).show();
          _added++;
          if (cnt == (collectionProperties.limit*1) - 1){
            _lastSection = $(item);
          }
        }
        else {
          _showMore = true;
        }
      });
      if (_added == 0){
        $(section).hide();
      }
      if (_showMore){
        $("<li>").addClass("facetShowMore").html('<a href="javascript:void(0)">${_('Show')} ' + ($(section).nextUntil(".facetHeader").length-(collectionProperties.limit*1)) + ' ${_('more...')}</a>').insertAfter(_lastSection);
      }
    });

    $(document).on("click", ".facetShowMore", function(){
      $(this).hide();
      $(this).nextUntil(".facetHeader").show();
    });

    $(".dateFacet").each(function () {
      var _m = moment($(this).text());
      var _em = moment($(this).text());
      var _format = $(this).data("format");
      var _gap = $(this).find(".dateFacetGap").text();
      var _how = _gap.match(/\d+/)[0];
      var _what = _gap.substring(_how.length + 1).toLowerCase();
      _em.add(_what, _how * 1);

      if (_format != null && _format != "") {
        if (_format.toLowerCase().indexOf("fromnow") > -1){
          $(this).text(_m.fromNow() + " - " + _em.fromNow());
        }
        else {
          $(this).text(_m.format(_format) + " - " + _em.format(_format));
        }
      }
      else {
        $(this).text(_m.format() + " - " + _em.format());
      }
      $(this).parents(".dateFacetItem").data("epoch", _m.valueOf());
    });

    var orderedDateFacets = $(".dateFacetItem");
    orderedDateFacets.sort(function (a, b) {
      a = $(a).data("epoch");
      b = $(b).data("epoch");
      if (a > b) {
        return -1;
      } else if (a < b) {
        return 1;
      } else {
        return 0;
      }
    });
    $(".dateFacetHeader").after(orderedDateFacets);

    % if hue_collection:
      $(".current-collection").text("${ hue_collection.label }");
      $("#id_collection").val(${ hue_collection.id });

      % if user.is_superuser:
        var collectionUrl = $(".dropdown-collection[data-value=${ hue_collection.id }]").data("settings-url");
        $(".change-settings").attr("href", collectionUrl);
      % endif
    % endif

    $(document).on("click", ".dropdown-collection", function (e) {
      e.preventDefault();
      var collectionId = $(this).data("value");
      $("select[name='collection']").val(collectionId);
      % if user.is_superuser:
        $(".change-settings").attr("href", $(this).data("settings-url"));
      % endif
      $.cookie("hueSearchLastCollection", collectionId, {expires: 90});
      $("form").find("input[type='hidden']").val("");
      $("form").submit();
      $(".selectMask").popover("hide");
    });

    $("#download-csv").on("click", function(e) {
      $("form").attr('action', "${ url('search:download', format='csv') }");
      $("form").attr('target', "_new");
      $("form").submit();
      $("form").removeAttr('action');
      $("form").removeAttr('target');
    });
    $("#download-xls").on("click", function(e) {
      $("form").attr('action', "${ url('search:download', format='xls') }");
      $("form").attr('target', "_new");
      $("form").submit();
      $("form").removeAttr('action');
      $("form").removeAttr('target');
    });

    function getCollectionPopoverContent() {
      var _html = "<ul class='unstyled'>";
      $("#collectionPopover ul li").each(function () {
        if ($(this).find("a").data("value") != $("#id_collection").val()) {
          _html += $(this).clone().wrap('<p>').parent().html();
        }
      });
      _html += "</ul>";
      return _html;
    }

    % if len(hue_collections) > 1:
    $(".selectMask").popover({
      html: true,
      content: getCollectionPopoverContent(),
      placement: "bottom"
    });
    % endif

    $("#recordsPerPage").change(function () {
      $("input[name='rows']").val($(this).val());
      $("input[name='rows']").closest("form").submit();
    });
    $("#recordsPerPage").val($("input[name='rows']").val());

    var sortingData = ${ hue_collection and hue_collection.sorting.data or '[]' | n,unicode };
    if (sortingData && sortingData.fields && sortingData.fields.length > 0) {
      $.each(sortingData.fields, function (index, item) {
        var _dropDownOption= $("<li>");
        _dropDownOption.html('<a href="#" class="dropdown-sort" data-field="'+ item.field +'" data-asc="'+ item.asc +'">'+ item.label +'</a>');
        _dropDownOption.appendTo($("#sortBy .dropdown-menu"));
      });
      var activeSorting = "${solr_query.get("sort", "")}";
      if (activeSorting == ""){
        // if the default sorting is just on one field, select that one
        var _defaultSorting = "";
        var _defaultSortingCnt = 0;
        $.each(sortingData.fields, function (index, item) {
          if (item.include) {
            _defaultSorting = item.label;
            _defaultSortingCnt++;
          }
        });
        if (_defaultSortingCnt == 1){
          $("#sortBy strong").text(_defaultSorting);
        }
      }
      if (activeSorting != "" && activeSorting.indexOf(" ") > -1) {
        $.each(sortingData.fields, function (index, item) {
          if (item.field == activeSorting.split(" ")[0] && item.asc == (activeSorting.split(" ")[1] == "asc")) {
            $("#sortBy strong").text(item.label);
          }
        });
      }
    }
    else {
      $("#sortBy").hide();
    }

    $(document).on("click", "#sortBy li a", function () {
      var _this = $(this);
      var _sort = _this.data("field") + "+" + (_this.data("asc") ? "asc" : "desc");
      if (typeof _this.data("field") == "undefined") {
        _sort = "";
      }
      location.href = "?query=${solr_query["q"]}&fq=${solr_query["fq"]}&rows=${solr_query["rows"]}&start=${solr_query["start"]}" + (_sort != "" ? "&sort=" + _sort : "");
    });

    $("#id_query").focus();

    $(document).on("keydown", function (e) {
      if (!e.ctrlKey && !e.altKey && !e.metaKey){
        if (!$("#id_query").is(":focus")) {
          $("#id_query").focus();
          $("#id_query").val($("#id_query").val());
        }
      }
    });

    $("#id_query").on("click", function (e) {
      if (e.pageX - $(this).position().left >= $(this).width()) {
        $(this).val("");
        $("#id_query").removeClass("deletable");
      }
    });

    $("#id_query").on("mousemove", function (e) {
      if (e.pageX - $(this).position().left >= $(this).width() && $(this).hasClass("deletable")) {
        $(this).css("cursor", "pointer");
      }
      else {
        $(this).css("cursor", "auto");
      }
    });

    if ($("#id_query").val().trim() != "") {
      $("#id_query").addClass("deletable");
    }

    % if hue_collection:
    $("#id_query").on("keyup", function() {
      var query = $("#id_query").val();
      if ($.trim(query) != "") {
        $("#id_query").addClass("deletable");
      }
      else {
        $("#id_query").removeClass("deletable");
      }
    });
    % endif

    % if hue_collection.autocomplete:
    $("#id_query").attr("autocomplete", "off");

    $("#id_query").jHueDelayedInput(function(){
      var query = $("#id_query").val();
      if (query) {
        $.ajax("${ url('search:query_suggest', collection_id=hue_collection.id) }" + query, {
          type: 'GET',
          success: function (data) {
            if (data.message.spellcheck && ! jQuery.isEmptyObject(data.message.spellcheck.suggestions)) {
              $('#id_query').typeahead({source: data.message.spellcheck.suggestions[1].suggestion});
            }
          }
        });
      }
    });
    % endif

    function getFq(existing, currentField, currentValue) {
      if (existing.indexOf(currentField) > -1) {
        var _pieces = existing.split("|");
        var _newPieces = [];
        $(_pieces).each(function (cnt, item) {
          if (item.indexOf(currentField) > -1) {
            _newPieces.push(currentField + currentValue);
          }
          else {
            // !!! High trickery. Uses jquery to reconvert all html entities to text
            _newPieces.push($("<span>").html(item).text());
          }
        });
        return _newPieces.join("|");
      }
      else {
        return $("<span>").html(existing).text() + "|" + currentField + currentValue;
      }
    }

    var _chartData = null;

    if ($(".chartComponent").length > 0){
      _chartData = eval($(".chartComponent").data("values"));
    }

    // test the content of _chartData to see if it can be rendered as chart
    if (_chartData != null && _chartData.length > 0) {
      if ($.isArray(_chartData[0])) {
        if ($.isNumeric(_chartData[0][0]) || _chartData[0][0].match(/[0-9][0-9][0-9][0-9]\-[0-9][0-9]\-[0-9][0-9]T/)) {
          var _isDate = false;
          if (_chartData[0][0].match(/[0-9][0-9][0-9][0-9]\-[0-9][0-9]\-[0-9][0-9]T/) != null){
            _isDate = true;
          }
          $(".chartComponent").jHueBlueprint({
            data: _chartData,
            label: $(".chartComponent").data("label"),
            type: $.jHueBlueprint.TYPES.BARCHART,
            color: $.jHueBlueprint.COLORS.BLUE,
            isDateTime: _isDate,
            fill: true,
            enableSelection: true,
            height: 100,
            onSelect: function (range) {
              var _start = Math.floor(range.xaxis.from)
              var _end = Math.ceil(range.xaxis.to);
              if (_isDate){
                _start = moment(range.xaxis.from).utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]");
                _end = moment(range.xaxis.to).utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]");
              }
              location.href = '?collection=${ current_collection }&query=${ solr_query['q'] }&fq=' + getFq("${ solr_query['fq'] }", $(".chartComponent").data("field"), ':["' + _start + '" TO "' + _end + '"]') + '${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}';
            },
            onItemClick: function (pos, item) {
              if (item) {
                $(".chartComponent").data("plotObj").highlight(item.series, item.datapoint);
                var _point = item.datapoint[0];
                if (_isDate){
                  var _momentDate = moment(item.datapoint[0]);
                  var _gap = $(".chartComponent").data("gap");
                  if (_gap != null && _gap != ""){
                    var _futureMomentDate = moment(item.datapoint[0]);
                    var _how = _gap.match(/\d+/)[0];
                    var _what = _gap.substring(_how.length + 1).toLowerCase();
                    _futureMomentDate.add(_what, _how * 1);
                    var _start = _momentDate.utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]");
                    var _end = _futureMomentDate.utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]");
                    location.href = '?collection=${ current_collection }&query=${ solr_query['q'] }&fq=' + getFq("${ solr_query['fq'] }", $(".chartComponent").data("field"), ':["' + _start + '" TO "' + _end + '"]') + '${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}';
                  }
                  else {
                    _point = '"' + _momentDate.utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]") + '"';
                    location.href = '?collection=${ current_collection }&query=${ solr_query['q'] }&fq=' + getFq("${ solr_query['fq'] }", $(".chartComponent").data("field"), ':' + _point) + '${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}';
                  }
                }
                else {
                  location.href = '?collection=${ current_collection }&query=${ solr_query['q'] }&fq=' + getFq("${ solr_query['fq'] }", $(".chartComponent").data("field"), ':' + _point) + '${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}';
                }
              }
            }
          });
        }
        else {
          $(".chartComponent").addClass("alert").text("${_('The graphical facets works just with numbers or dates. Please choose another field.')}")
        }
      }
      else {
        $(".chartComponent").addClass("alert").text("${_('There was an error initializing the graphical facet component.')}")
      }
    }
    else {
      $(".chartComponent").hide();
    }

  });
</script>

${ commonfooter(messages) | n,unicode }
